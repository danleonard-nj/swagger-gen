from typing import List, Union
from swagger_gen.lib.constants import (
    SchemaDefinition,
    Meta
)
from swagger_gen.lib.endpoint import Endpoint
from swagger_gen.lib.exceptions import NullReferenceException
from swagger_gen.lib.metadata import EndpointMetadata
from swagger_gen.lib.utils import empty


class SwaggerDefinition:
    def __init__(self, app_name: str, app_version: str):
        self.app_name = app_name
        self.app_version = app_version

        self._definition = self._get_base_definition()
        self._metadata = EndpointMetadata()

    def get_definition(self) -> dict:
        '''
        Return the generated Swagger definition

        returns:
            (dict) Swagger definitions
        '''

        return self._definition

    def add_endpoint(self, endpoint: Endpoint) -> None:
        '''
        Parse an endpoint and add it to to Swagger definitions

        params:
            endpoint    :   endpoint to parse
        '''

        # TODO: Pass down optional responses param to _create_path

        self._create_path(endpoint)

    def _add_path(self, endpoint_literal: str, definition: dict):
        '''
        Add the generated endpoint path schema to the Swagger
        definition 

        params:
            endpoint_literal    :   the endpoint url
            definition          :   the endpoint path schema
        '''

        self._definition['paths'][endpoint_literal] = definition

    def _add_component(self, component_key: str, component_model: dict):
        '''
        Add the generated component schema to the Swagger
        definition.  The component key links the endpoint
        path definition to the component schema

        The component model descriptors are key : datatype

        {
            'name' : 'string',
            'date' : 'datetime'
        }

        params:
            component_key       :   the endpoint component key
            component_model     :   the component model of 
                                    endpoint request body
        '''

        self._definition['components']['schemas'][component_key] = component_model

    def _create_path(self, endpoint: Endpoint, responses: dict = None) -> None:
        '''
        Generate the endpoint path schema.  This incorporates any optional 
        metadata that is defined on the endpoint by way of @swagger_metadata.

        params:
            endpoint    :   the endpoint to parse
            responses   :   the endpoint response models.  This defaults to
                            a model indicating a 200 OK response
        '''

        definition = dict()

        for method in endpoint.methods:
            method_definition = self._get_base_method_definition(
                endpoint=endpoint,
                responses=responses)

            metadata = self._metadata.get_endpoint_metadata(
                endpoint=endpoint.metadata_key)
            has_metadata = metadata is not None

            parameters = list()
            if not empty(endpoint.segment_params):
                self._add_path_parameters(
                    endpoint=endpoint,
                    parameters=parameters)
            if has_metadata:
                self._add_metadata(
                    method_definition=method_definition,
                    endpoint=endpoint,
                    metadata=metadata,
                    parameters=parameters)

            if not empty(parameters):
                method_definition[SchemaDefinition.PARAMETERS] = parameters

        definition[method.lower()] = method_definition
        self._add_path(
            endpoint_literal=endpoint.endpoint_literal,
            definition=definition)

    def _get_base_method_definition(self, endpoint: Endpoint, responses: dict) -> dict:
        return {
            SchemaDefinition.ENDPOINT_TAGS: [endpoint.tag]
        }

    def _add_path_parameters(self, endpoint, parameters) -> None:
        path_parameters = (
            [
                self._create_parameter_definition(
                    arg, Meta.PARAM_PATH_TYPE)
                for arg in endpoint.segment_params
            ])
        parameters.extend(path_parameters)

    def _add_metadata(self, endpoint, metadata, parameters, method_definition: dict) -> None:
        endpoint_model = metadata.get(
            Meta.MODEL_KEY)
        endpoint_query_params = metadata.get(
            Meta.QUERY_PARAM_KEY)
        endpoint_description = metadata.get(
            Meta.DESCRIPTION_KEY)
        endpoint_summary = metadata.get(
            Meta.SUMMARY_KEY)
        endpoint_responses = metadata.get(
            Meta.RESPONSES_KEY)

        # If query parameters are defined in the metadata
        if endpoint_query_params:
            query_parameters = (
                [
                    self._create_parameter_definition(
                        arg, Meta.PARAM_QUERY_TYPE)
                    for arg in self._get_query_params(endpoint)
                ])
            parameters.extend(query_parameters)

        # If a request model is defined in the metadata
        if endpoint_model:
            method_definition[SchemaDefinition.REQUEST_BODY] = (
                self._get_model_reference(endpoint=endpoint))

            self._add_component(
                component_key=endpoint.component_key,
                component_model=self._get_model_component_schema(
                    model=endpoint_model))

        # If there are respones defined in the metadata, use those.  Otherwise set defaults
        if endpoint_responses:
            _endpoint_responses = endpoint_responses
        else:
            _endpoint_responses = self._get_default_responses()
        method_definition[SchemaDefinition.ENDPOINT_RESPONSES] = _endpoint_responses

        # If there are endpoint descriptions provided
        if endpoint_description:
            method_definition[SchemaDefinition.DESCRIPTION] = endpoint_description

        # If there are endpoint descriptions provided
        if endpoint_summary:
            method_definition[SchemaDefinition.SUMMARY] = endpoint_summary

    def _get_base_definition(self) -> dict:
        '''
        Get the base Swagger definition schema.  This is boilerplate,
        additional fields can be added elsewhere (servers, etc)
        '''

        return {
            'openapi': SchemaDefinition.OPEN_API_VERSION,
            'info': {
                'title': self.app_name,
                'version': self.app_version
            },
            'paths': {},
            'components': {
                'schemas': {}
            }
        }

    def _get_default_responses(self):
        '''
        Get the default endpoint response model.  Additional responses
        can be defined to bypass default values in create_endpoint()
        '''

        # TODO: Pass down responses from create_endpoint -> _create_path, etc

        return {
            '200': {
                'description': 'Success'
            }
        }

    def _get_model_reference(self, endpoint: Endpoint) -> Union[dict, None]:
        if (self._metadata.get_endpoint_metadata(endpoint.metadata_key)
                and self._metadata.get_endpoint_metadata(endpoint.metadata_key).get(
                    Meta.MODEL_KEY)):

            return {
                'content': {
                    'application/json': {
                        'schema': {
                            '$ref': f'#/components/schemas/{endpoint.component_key}'
                        }
                    }
                }
            }

    def _get_model_component_schema(self, model: dict) -> dict:
        if not model:
            raise NullReferenceException('model')

        props = dict()
        for prop in model:
            props[prop] = {
                'type': model[prop],
                'nullable': True
            }

        model_metadata = {
            'type': 'object',
            'properties': props
        }

        return model_metadata

    def _create_parameter_definition(self, name: str, _in: str, required=True) -> dict:
        if not name:
            raise NullReferenceException('name')
        if not _in:
            raise NullReferenceException('_in')

        return {
            'name': name,
            'in': _in,
            'required': required,
            'schema': {
                'type': 'string',
                'nullable': False
            }
        }

    def _get_query_params(self, endpoint: Endpoint):
        if self._metadata.get_endpoint_metadata(endpoint.metadata_key):
            query_parameters = self._metadata.get_endpoint_metadata(
                endpoint.metadata_key).get(Meta.QUERY_PARAM_KEY)

            if query_parameters:
                return query_parameters
