import redis


client = redis.Redis(host='localhost', port=6379)


def cache_result(key, value):
    client.set(key, value)


def get_result(key):
    return client.get(key)
