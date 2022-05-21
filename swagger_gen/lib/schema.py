from swagger_gen.lib.constants import (
    AuthType,
    ComponentType,
    ContentType,
    Meta,
    ParameterType,
    Schema,
)
from typing import List, Union
from swagger_gen.lib.endpoint import SwaggerEndpoint
from swagger_gen.lib.metadata import EndpointMetadata
from swagger_gen.lib.wrappers import get_endpoint_metadata
from swagger_gen.lib.utils import (
    element_at,
    first,
    validate_constant,
    defined,
    is_type,
    not_null,
)


class SwaggerDefinition:
    '''
    The definition buildup utility.  This should not be long for this world.
    Improvements can be made to pull this apart into classes that handle their
    own schema generation, i.e. SwaggerQueryParam..  There are a handful of 
    clear benefits from this:
        - Less likely to break shit in the schema
        - Separate implementation details.  i.e. generic schema objects that
        should be interchangable to generate JSON, YAML, etc.
        - generating the schema can be hidden.
    '''

    def __init__(
            self,
            app,
            **kwargs):

        not_null(app, 'app')

        self._app = app

        self._app_name = kwargs.get('title') or self._app.__name__
        self._app_version = kwargs.get('version')
        self._url = kwargs.get('url') or '/swagger'
        self._app_terms_of_service = kwargs.get('terms_of_service')
        self._app_description = kwargs.get('description')
        self._app_contact_email = kwargs.get('contact_email')
        self._app_license_name = kwargs.get('license_name')
        self._app_license_url = kwargs.get('license_url')
        self._app_external_doc_description = kwargs.get(
            'external_doc_description')
        self._app_external_doc_url = kwargs.get('external_doc_url')
        self._app_servers = kwargs.get('servers')
        self._app_auth_schemes = kwargs.get('auth_schemes')

        is_type(self._app_servers, 'auth_schemes', list)
        is_type(self._app_servers, 'servers', list)
        is_type(self._app_external_doc_url, 'license_url', str)
        is_type(self._app_external_doc_description, 'license_url', str)
        is_type(self._app_license_url, 'license_url', str)
        is_type(self._app_license_name, 'license_name', str)
        is_type(self._app_contact_email, 'contact_email', str)
        is_type(self._app_description, 'description', str)
        is_type(self._app_terms_of_service, 'terms_of_service', str)

        self._definition = self._get_base_definition()

    def get_definition(self) -> dict:
        '''
        Return the generated Swagger definition

        returns:
        `dict`: Swagger definitions
        '''

        return self._definition

    def add_endpoint(
            self,
            endpoint: SwaggerEndpoint) -> None:
        '''
        Parse an endpoint and add it to to Swagger definitions

        params:
        `endpoint` : endpoint to parse
        '''

        not_null(endpoint, 'endpoint')

        # TODO: Pass down optional responses param to _create_path

        self._create_endpoint_definition(endpoint)

    def _add_path(
            self,
            endpoint_literal: str,
            definition: dict) -> None:
        '''Add the generated endpoint path schema to the Swagger definition'''

        not_null(endpoint_literal, 'endpoint_literal')
        not_null(definition, 'definition')

        # If we've already defined a method on this endpoint literal, we'll need to
        # add the supplied definitions to the existing endpoint definition.
        if self._definition[Schema.PATHS].get(endpoint_literal):
            for method in definition.keys():
                self._definition[Schema.PATHS][endpoint_literal][method] = definition[method]

        # If this is the first or only endpoint definition, just set it on the key
        else:
            self._definition[Schema.PATHS][endpoint_literal] = definition

    def _add_component(
            self,
            component_key: str,
            component_type: str,
            component_model: dict):
        '''Add the generated component schema to the definition'''

        not_null(component_key, 'component_key')
        not_null(component_type, 'component_type')
        not_null(component_model, 'component_model')

        # Set an empty dictionary if the section doesn't exist yet for the specified
        # component type
        if self._definition[Schema.COMPONENTS].get(component_type) is None:
            self._definition[Schema.COMPONENTS][component_type] = dict()

        self._definition[Schema.COMPONENTS][component_type][component_key] = component_model

    def _create_endpoint_definition(
            self,
            endpoint: SwaggerEndpoint) -> None:
        ''' Generate the endpoint definition from the provided SwaggerEndpoint '''

        not_null(endpoint, 'endpoint')
        definition = dict()

        # If there are auth schemes defined, parse and add them to the components
        # section
        if (defined(self._app_auth_schemes)
                and any(self._app_auth_schemes)):
            self._create_auth_section()

        # There can be multiple methods per endpoint, each with their own definition
        for method in endpoint.methods:

            # Start with the endpoint tag, or the 'section' the endpoint will be displayed
            # under in the Swagger UI
            method_definition = {
                Schema.ENDPOINT_TAGS: [endpoint.tag]
            }

            # Fetch any defined route metadata from the metadata collection.  When the
            # app starts and routes are registered, we build out the route metadata from
            # details provided on the wrappers (swagger_metadata, etc).  Since this occurs
            # before `werkzeug` maps are available (which the base documentation is parsed
            # from) it's stored in a global MetadataCollection instance, and fetched here
            # by the view function name as the key
            metadata = get_endpoint_metadata(
                view_function_name=endpoint.view_function_name)

            # Handle the route segments.  These have to be modified slightly
            # from Flask's formatting to match Swagger conventions.  Basically
            # just swapping the carats for curly braces
            parameters = list()
            if not any(endpoint.segment_params):

                # Generate the documentation for the route segment
                path_parameters = (
                    [
                        self._create_parameter_definition(
                            arg, Meta.PARAM_PATH_TYPE)
                        for arg in endpoint.segment_params
                    ])

                parameters.extend(path_parameters)

            # If the endpoint has metadata defined, parse it and include it in the
            # definition
            if metadata is not None:
                self._add_metadata(
                    method_definition=method_definition,
                    endpoint=endpoint,
                    metadata=metadata,
                    parameters=parameters)

            # Add generic metadata if it's not defined on the route
            else:
                defaults = self._get_default_metadata()
                method_definition = method_definition or defaults

            if not any(parameters):
                method_definition[Schema.PARAMETERS] = parameters

        # Set the method definition on the endpoint definition using the lowered
        # method name
        definition[method.lower()] = method_definition

        # Add the endpoint definition to the spec
        self._add_path(
            endpoint_literal=endpoint.endpoint_literal,
            definition=definition)

    def _get_default_metadata(self):
        _metadata = dict()
        _metadata[Schema.ENDPOINT_RESPONSES] = self._get_default_responses()

        return _metadata

    def _get_base_method_definition(self, endpoint: SwaggerEndpoint) -> dict:
        '''
        Get the base definition for the endpoint request method.
        '''

        not_null(endpoint, 'endpoint')

        is_type(endpoint, 'endpoint', SwaggerEndpoint)

        # TODO: This can probably be ditched and inclued somewhere else.
        # there used to be more going on in here

        return {
            Schema.ENDPOINT_TAGS: [endpoint.tag]
        }

    def _add_metadata(
            self,
            endpoint: SwaggerEndpoint,
            metadata: EndpointMetadata,
            parameters: List,
            method_definition: dict) -> None:
        '''
        Add any defined metadata for the endpoint to the definition
        '''

        not_null(endpoint, 'endpoint')
        not_null(metadata, 'metadata')
        not_null(method_definition, 'method_definition')

        # Validate types
        is_type(endpoint, 'endpoint', SwaggerEndpoint)
        is_type(metadata, 'metadata', EndpointMetadata)
        is_type(parameters, 'parameters', list, null=True)
        is_type(method_definition, 'method_definition', dict)

        # If query parameters are defined in the metadata, parse them and add to the
        # endpoint definition.
        if metadata.query_params:
            query_parameters = (
                [
                    self._create_parameter_definition(
                        name=arg,
                        parameter_type=ParameterType.QUERY)
                    for arg in metadata.query_params
                ])
            parameters.extend(query_parameters)

        # If a request model is defined in the metadata
        if metadata.request_model:
            method_definition[Schema.REQUEST_BODY] = (
                self._get_model_reference(endpoint=endpoint))

            # Add the model to the component section of the documentation.  The models
            # representing the requests are stored under 'components', and on the route
            # that implements them, a reference to that component is provided
            self._add_component(
                component_type=ComponentType.SCHEMAS,
                component_key=endpoint.component_key,
                component_model=self._get_model_component_schema(
                    model=metadata.request_model))

        # If there are respones defined in the metadata, use those
        if metadata.response_model:
            method_definition[Schema.ENDPOINT_RESPONSES] = (
                self._format_response(
                    response=metadata.response_model)
            )

        # Otherwise just use some default values (200, success)
        else:
            method_definition[Schema.ENDPOINT_RESPONSES] = (
                self._get_default_responses()
            )

        # If there are endpoint descriptions provided.  The endpoint description
        # is displayed in the expanded endpoint accordion
        if metadata.description:
            method_definition[Schema.DESCRIPTION] = metadata.description
        else:
            method_definition[Schema.DESCRIPTION] = endpoint.view_function_name

        # If there is an endpoint summary provided.  The summary is displayed in
        # the collapsed endpoint accordion, adjacent to the route
        if metadata.summary:
            method_definition[Schema.SUMMARY] = metadata.summary

        # If there are security schemes defined, include them on the endpoint
        if metadata.security:
            # If no schemes are defined
            if not defined(self._app_auth_schemes):
                raise Exception('No security schemes are defined')

            # If the requested scheme is not defined
            security_schema = first(
                self._app_auth_schemes,
                lambda x: x.name == metadata.security)

            if security_schema is None:
                raise Exception(
                    f"No scheme with the name '{metadata.security}' is defined")

            # Include the scopes for the OAuth schemes
            if security_schema.auth_type == AuthType.OAUTH_2:
                if not defined(metadata.scopes):
                    raise Exception(
                        'Scopes must be provided when using an OAuth flow')

                method_definition[Schema.SECURITY] = [{
                    metadata.security: metadata.scopes
                }]

            # Other methods can take an empty list
            else:
                method_definition[Schema.SECURITY] = [{
                    metadata.security: []
                }]

    def _get_base_definition(self) -> dict:
        '''
        Get the boilerplate definition schema.  This serves as the base for the Swagger
        definitions, where paths and component schemas are populated during the buildup
        '''

        base = {
            Schema.OPEN_API: Schema.OPEN_API_VERSION,
            Schema.PATHS: {},
            Schema.COMPONENTS: {
                Schema.SCHEMAS: {}
            }
        }

        # The title is the only required value here, if it isn't provided during buildup
        # we'll use the app name
        info = {
            Schema.TITLE: self._app_name
        }

        # Description
        if defined(self._app_description):
            info[Schema.DESCRIPTION] = self._app_description

        # Contact info
        if defined(self._app_contact_email):
            info[Schema.CONTACT] = {
                Schema.EMAIL: self._app_contact_email
            }

        # Terms of service
        if defined(self._app_terms_of_service):
            info[Schema.TERMS_OF_SERVICE] = self._app_terms_of_service

        # License info
        if (defined(self._app_license_name)
                and defined(self._app_license_url)):
            info[Schema.LICENSE] = {
                Schema.NAME: self._app_license_name,
                Schema.URL: self._app_license_url
            }

        # External documentation
        if (defined(self._app_external_doc_description)
                and defined(self._app_external_doc_url)):
            base[Schema.EXTERNAL_DOCS] = {
                Schema.URL: self._app_external_doc_description,
                Schema.NAME: self._app_external_doc_url
            }

        # Servers
        if (defined(self._app_servers)):
            base[Schema.SERVERS] = [
                {Schema.URL: srv}
                for srv in self._app_servers
            ]

        base[Schema.INFO] = info
        return base

    def _get_default_responses(self):
        '''The default endpoint responses, used if no others are defined'''

        # TODO: Pass down responses from create_endpoint -> _create_path, etc

        return {
            '200': {
                Schema.DESCRIPTION: 'Success'
            }
        }

    def _get_model_reference(
            self,
            endpoint: SwaggerEndpoint) -> Union[dict, None]:
        '''Get the endpoint request model definition to be included in the definition components'''

        not_null(endpoint, 'endpoint')

        return {
            Schema.CONTENT: {
                ContentType.APPLICATION_JSON: {
                    Schema.SCHEMA: {
                        Schema.REF: f'#/components/schemas/{endpoint.component_key}'
                    }
                }
            }
        }

    def _get_model_component_schema(
            self,
            model: dict) -> dict:
        '''Generate the endpoint request model component schema'''

        not_null(model, 'model')
        is_type(model, 'model', dict)

        props = dict()
        for prop in model:
            props[prop] = {
                Schema.PROPERTY_TYPE: model[prop],
                Schema.NULLABLE: True
            }

        model_metadata = {
            Schema.PROPERTY_TYPE: 'object',
            Schema.PROPERTIES: props
        }

        return model_metadata

    def _format_response(self, response: List[tuple]) -> dict:
        '''
        Format response definitions for the Swagger documentation
        '''

        # TODO: Verify status code cardinality as it's used as a key
        _responses = dict()
        is_type(response, 'response', list)

        for descriptor in response:
            # Verify the response descriptor contains both the status and description
            if len(descriptor) != 2:
                raise Exception(f'''
                    Invalid response definition.  The response must either be a list of tuples
                    or a single tuple with a status code and a description describing the status''')

            _status_code = str(element_at(descriptor, 0))
            _responses[_status_code] = {
                Schema.DESCRIPTION: element_at(descriptor, 1)
            }

        return _responses

    def _create_parameter_definition(
            self,
            name: str,
            parameter_type: str,
            required=True) -> dict:
        '''
        Generate an endpoint paramaeter definition

        params:
        `name`: the name of the query parameter
        `parameter_type`: the type of parameter. These are defined in the `ParameterType` constants
        '''

        not_null(name, 'name')
        not_null(parameter_type, 'parameter_type')

        is_type(name, 'name', str)
        is_type(parameter_type, 'parameter_type', str)
        is_type(required, 'required', bool)

        # Validate parameter type options
        validate_constant(ParameterType, parameter_type)

        return {
            Schema.NAME: name,
            Schema.IN: parameter_type,
            Schema.REQUIRED: required,
            Schema.SCHEMA: {
                Schema.PROPERTY_TYPE: 'string',
                Schema.NULLABLE: False
            }
        }

    def _create_auth_section(self) -> dict:
        '''Generate the spec for the auth schemes'''

        for auth_scheme in self._app_auth_schemes:
            self._add_component(
                component_key=auth_scheme.name,
                component_type=ComponentType.SECURITY_SCHEMES,
                component_model=auth_scheme._to_spec()
            )
