class MethodEnum:
    '''
    Request methods
    '''

    GET = 'GET'
    PUT = 'PUT'
    DELETE = 'DELETE'
    POST = 'POST'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'


class DefinitionEnum:
    '''
    Definition file constants
    '''

    PATHS = 'paths'
    COMPONENTS = 'components'
    COMPONENTS_SCHEMAS = 'schemas'
    PARAMETERS = 'parameters'
    REQUEST_BODY = 'requestBody'
    ENDPOINT_TAGS = 'tags'
    ENDPOINT_RESPONSES = 'responses'
    OPEN_API_VERSION = '3.0.1'
    BEARER = 'bearerAuth'


class MetadataEnum:
    '''
    Metadata constants
    '''

    QUERY_PARAM_KEY = 'query_params'
    MODEL_KEY = 'model'
    SECURITY_KEY = 'security'
    PARAM_PATH_TYPE = 'path'
    PARAM_QUERY_TYPE = 'query'
    REQUEST_BODY = 'request_body'


class DependencyEnum:
    '''
    Dependency constants
    '''

    PKG_SWAG_UI = 'index.html'
    PKG_RESOURCE_MODULE = 'swagger_gen.resources'
    PKG_SWAGGER = 'swagger.pkl'


class RouteEnum:
    '''
    Route constants
    '''

    SWAG_DEPS_BASE = '/swagger/<resource_name>'
    SWAG_INDEX_DEFAULT = '/swagger/index.html'


class SecurityEnum:
    '''
    Security constants
    '''

    BEARER_SCHEME = 'bearer'
    BEARER_FORMAT_JWT = 'JWT'
    JWT_SCHEME = 'bearerAuth'
    API_KEY_SCHEME = 'apiKey'


class JwtScheme:
    TYPE = 'bearer'
    FORMAT = 'JWT'
    SCHEME = 'bearerAuth'
    DESCRIPTION = 'JWT Bearer authentication scheme'
