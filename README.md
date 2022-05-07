# CPSC612_Translator_Application

## Installation
In order to run the application, two docker containers must first be started. Navigate to the `translator/model` 
directory and execute the following commands:
````bash
docker run -d --rm -p 9000:9000 -v ${PWD}:/models --name tensorflow_serving --entrypoint tensorflow_model_server tensorflow/serving:2.3.0 --enable_batching=true --batching_parameters_file=/models/batching_parameters.txt --port=9000 --model_base_path=/models/ende --model_name=ende
docker run -d -p 6379:6379 --name redis redis
````

Next, the requirements can be installed by navigating to the root of the repository and executing `pip install -e .`.
Finally, the FastAPI server can be started by executing `python translator/__init__.py`.

## Usage
Navigate to `http://localhost:8000` and enter a word or phrase that you'd like to translate from English to German.