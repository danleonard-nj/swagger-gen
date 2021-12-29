from functools import wraps

endpoint_metadata = dict()


class EndpointMetadata:
    def get_endpoint_metadata(self, endpoint: str):
        return endpoint_metadata.get(endpoint)


def swagger_metadata(**kwargs):
    def real_decorator(function):
        endpoint_metadata[function.__name__] = kwargs

        @wraps(function)
        def wrapper(*_args, **_kwargs):
            return function(*_args, **_kwargs)
        return wrapper
    return real_decorator
