
class Method:
    '''
    Request methods
    '''

    GET = 'GET'
    PUT = 'PUT'
    DELETE = 'DELETE'
    POST = 'POST'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    PATCH = 'PATCH'


# class Response:
#     OK = 200, 'OK'
#     NO_CONTENT = 201
#     BAD_REQUEST = 400
#     UNAUTHORIZED = 401
#     FORBIDDEN = 403
#     INTERNAL_SERVER_ERROR = 500

#     Description = {
#         OK: '200 Ok',
#         NO_CONTENT: '201 No Content',
#         BAD_REQUEST: '400 Bad Request',
#         UNAUTHORIZED: '401 Unauthorized',
#         FORBIDDEN: '403 Forbidden',
#         INTERNAL_SERVER_ERROR: '500 Internal Server Error'
#     }


class SchemaDefinition:
    '''
    Definition file constants
    '''

    PATHS = 'paths'
    COMPONENTS = 'components'
    COMPONENTS_SCHEMAS = 'schemas'
    PARAMETERS = 'parameters'
    SUMMARY = 'summary'
    DESCRIPTION = 'description'
    REQUEST_BODY = 'requestBody'
    ENDPOINT_TAGS = 'tags'
    ENDPOINT_RESPONSES = 'responses'
    OPEN_API_VERSION = '3.0.1'
    BEARER = 'bearerAuth'


class Meta:
    '''
    Metadata constants
    '''

    QUERY_PARAM_KEY = 'query_params'
    MODEL_KEY = 'model'
    SECURITY_KEY = 'security'
    RESPONSES_KEY = 'responses'
    DESCRIPTION_KEY = 'description'
    SUMMARY_KEY = 'summary'
    PRODUCES_KEY = 'produces'
    PARAM_PATH_TYPE = 'path'
    PARAM_QUERY_TYPE = 'query'
    REQUEST_BODY = 'request_body'


class DependencyInfo:
    '''
    Dependency constants
    '''

    PKG_SWAG_UI = 'index.html'
    PKG_RESOURCE_MODULE = 'swagger_gen.resources'
    PKG_SWAGGER = 'swagger.pkl'


class SwaggerRoute:
    '''
    Route constants
    '''

    SWAG_DEPS_BASE = '/swagger/<resource_name>'
    SWAG_INDEX_DEFAULT = '/swagger/index.html'


class SecurityDefinition:
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
