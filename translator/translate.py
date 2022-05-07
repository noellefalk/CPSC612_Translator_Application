"""Controller that interfaces with the pretrained model to complete translation
Controller code for sending requests to the model was adapted from examples provided by OpenNMT
https://github.com/OpenNMT/OpenNMT-tf/tree/master/examples/serving/tensorflow_serving"""


import grpc
import pyonmttok
import tensorflow as tf
from translator.model import MAIN_DIRECTORY
from translator.redis_cache import cache_result, get_result

from tensorflow_serving.apis import predict_pb2, prediction_service_pb2_grpc


def pad_batch(batch_tokens):
    """Pads a batch of tokens."""
    lengths = [len(tokens) for tokens in batch_tokens]
    max_length = max(lengths)
    for tokens, length in zip(batch_tokens, lengths):
        if max_length > length:
            tokens += [""] * (max_length - length)
    return batch_tokens, lengths, max_length


def extract_prediction(result):
    """Parses a translation result.
    Args:
      result: A `PredictResponse` proto.
    Returns:
      A generator over the hypotheses.
    """
    batch_lengths = tf.make_ndarray(result.outputs["length"])
    batch_predictions = tf.make_ndarray(result.outputs["tokens"])
    for hypotheses, lengths in zip(batch_predictions, batch_lengths):
        # Only consider the first hypothesis (the best one).
        best_hypothesis = hypotheses[0].tolist()
        best_length = lengths[0]
        if best_hypothesis[best_length - 1] == b"</s>":
            best_length -= 1
        yield best_hypothesis[:best_length]


def send_request(stub, model_name, batch_tokens, timeout=5.0):
    """Sends a translation request.
    Args:
      stub: The prediction service stub.
      model_name: The model to request.
      tokens: A list of tokens.
      timeout: Timeout after this many seconds.
    Returns:
      A future.
    """
    batch_tokens, lengths, max_length = pad_batch(batch_tokens)
    batch_size = len(lengths)
    request = predict_pb2.PredictRequest()
    request.model_spec.name = model_name
    request.inputs["tokens"].CopyFrom(
        tf.make_tensor_proto(
            batch_tokens, dtype=tf.string, shape=(batch_size, max_length)
        )
    )
    request.inputs["length"].CopyFrom(
        tf.make_tensor_proto(lengths, dtype=tf.int32, shape=(batch_size,))
    )
    return stub.Predict.future(request, timeout)


def translate(user_input, timeout=30.0):
    """Translates user input (words or sentences).
    Args:
      user_input: A list of sentences.
      timeout: Timeout after this many seconds.
    Variable Definitions:
      stub: The prediction service stub.
      model_name: The model to request. ende = English to Deutsch
      tokenizer: The tokenizer to apply.
    Returns:
      A generator over the detokenized predictions.
    """
    result = get_result(user_input[0])
    if result is not None:
        return [result]
    channel = grpc.insecure_channel("%s:%d" % ('localhost', 9000))
    stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    tokenizer = pyonmttok.Tokenizer("none", sp_model_path=f'{MAIN_DIRECTORY}/ende/1/assets.extra/wmtende.model')
    model_name = 'ende'

    batch_input = [tokenizer.tokenize(text)[0] for text in user_input]
    future = send_request(stub, model_name, batch_input, timeout=timeout)
    result = future.result()
    translated_output = [
        tokenizer.detokenize(prediction) for prediction in extract_prediction(result)
    ]
    cache_result(user_input[0], translated_output[0])
    return translated_output

