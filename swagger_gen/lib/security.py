from swagger_gen.lib.constants import AuthType
from swagger_gen.lib.utils import element_at, not_null


class AuthBase:
    def _to_spec(self) -> dict:
        pass


class BearerAuth(AuthBase):
    def __init__(self, name):
        self.auth_type = AuthType.HTTP
        not_null(name, 'name')

        self.name = name

    def _to_spec(self):
        return {
            'type': AuthType.HTTP,
            'scheme': 'bearer',
            'bearerFormat': 'JWT'
        }


class ApiKey(AuthBase):
    def __init__(self, name, header_key):
        self.auth_type = AuthType.API_KEY
        not_null(name, 'name')
        not_null(header_key, 'header_key')

        self.name = name

        self._header_key = header_key

    def _to_spec(self):
        return {
            'type': AuthType.API_KEY,
            'name': self._header_key,
            'in': 'header'
        }


class OAuth(AuthBase):
    def __init__(self, name, auth_url, scopes: list[tuple]):
        self.auth_type = AuthType.OAUTH_2
        not_null(name, 'name')
        not_null(auth_url, 'auth_url')
        not_null(scopes, 'scopes')

        self.name = name

        self._auth_url = auth_url
        self._scopes = scopes

    def _to_spec(self):
        '''Generate the Swagger document spec'''
        return {
            'type': AuthType.OAUTH_2,
            'flows': {
                'implicit': {
                    'authorizationUrl': self._auth_url,
                    'scopes': self._parse_scopes_spec(self._scopes)}
            }
        }

    def _parse_scopes_spec(self, scopes: list[tuple]):
        '''Parse the service scopes from tuples to the document spec'''

        _scopes = dict()
        for scope in scopes:
            # Validate scope comforms to requirements
            if len(scope) != 2:
                raise Exception('''Invalid scope descriptior, must be a tuple that contains
                the scope name and a description of the scope''')

            # Set the scope and description spec
            _scopes[scope] = {
                element_at(scope, 0): element_at(scope, 1)
            }

        return _scopes
