from functools import wraps

endpoint_metadata = dict()


def format_response(status_code, description):
    return {
        'responses': [{
            str(status_code): {
                'description': description
            }
        }]
    }


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


def swagger_response(status_code, description):
    def real_decorator(function):
        response = format_response(
            status_code=status_code,
            description=description)

        if not endpoint_metadata.get(function.__name__):
            endpoint_metadata[function.__name__] = {
                'responses': [response]
            }

        else:
            _meta = endpoint_metadata[function.__name__]
            if not _meta.get('responses'):
                _meta['responses'] = [response]
            else:
                _meta['responses'].append(response)

        @wraps(function)
        def wrapper(*_args, **_kwargs):
            return function(*_args, **_kwargs)
        return wrapper
    return real_decorator
