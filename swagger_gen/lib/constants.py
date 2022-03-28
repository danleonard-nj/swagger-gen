
class Method:
    '''Request methods'''

    GET = 'GET'
    PUT = 'PUT'
    DELETE = 'DELETE'
    POST = 'POST'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    PATCH = 'PATCH'


class Schema:
    '''Spec file key constants'''

    PATHS = 'paths'
    TITLE = 'title'
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
    CONTACT = 'contact'
    EMAIL = 'email'
    TERMS_OF_SERVICE = 'termsOfService'
    LICENSE = 'license'
    NAME = 'name'
    URL = 'url'
    EXTERNAL_DOCS = 'externalDocs'
    SERVERS = 'servers'
    INFO = 'info'
    SECURITY = 'security'
    OPEN_API = 'openapi'
    PATHS = 'paths'
    COMPONENTS = 'components'
    SCHEMAS = 'schemas'
    SCHEMA = 'schema'
    CONTENT = 'content'
    REF = '$ref'
    PROPERTY_TYPE = 'type'
    NULLABLE = 'nullable'
    PROPERTIES = 'properties'
    IN = 'in'
    REQUIRED = 'required'


class AuthType:
    '''Auth type constants'''

    API_KEY = 'apiKey'
    OAUTH_2 = 'oauth2'
    HTTP = 'http'


class ComponentType:
    '''Spec component section constants'''

    SCHEMAS = 'schemas'
    SECURITY_SCHEMES = 'securitySchemes'


class ParameterType:
    '''URL segment/query param constants'''

    PATH = 'path'
    QUERY = 'query'


class Meta:
    '''Metadata constants'''

    QUERY_PARAM_KEY = 'query_params'
    MODEL_KEY = 'model'
    PARAM_PATH_TYPE = 'path'
    REQUEST_BODY = 'request_body'


class DependencyInfo:
    '''Dependency constants'''

    PKG_RESOURCE_MODULE = 'swagger_gen.resources'
    PKG_SWAGGER = 'swagger.pkl'


class ContentType:
    '''Content type constants'''
    APPLICATION_JSON = 'application/json'
    TEXT_CSS = 'text/css'
    JAVASCRIPT = 'text/javascript'
