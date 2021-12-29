from typing import Union
from swagger_gen.lib.constants import (
    DefinitionEnum,
    MetadataEnum
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

    def get_definition(self):
        return self._definition

    def add_endpoint(self, endpoint: Endpoint):
        self._create_path(endpoint)

    def _add_path(self, endpoint, definition):
        self._definition['paths'][endpoint] = definition

    def _add_component(self, name: str, model: dict):
        self._definition['components']['schemas'][name] = model

    def _create_path(self, endpoint: Endpoint, responses=None):
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
                method_definition[DefinitionEnum.PARAMETERS] = parameters

        definition[method.lower()] = method_definition
        self._add_path(
            endpoint=endpoint.endpoint_literal,
            definition=definition)

    def _get_base_method_definition(self, endpoint: Endpoint, responses):
        return {
            DefinitionEnum.ENDPOINT_TAGS: [endpoint.tag],
            DefinitionEnum.ENDPOINT_RESPONSES: (
                responses or self._get_default_responses())
        }

    def _add_path_parameters(self, endpoint, parameters) -> None:
        path_parameters = (
            [
                self._create_parameter_definition(
                    arg, MetadataEnum.PARAM_PATH_TYPE)
                for arg in endpoint.segment_params
            ])
        parameters.extend(path_parameters)

    def _add_metadata(self, endpoint, metadata, parameters, method_definition: dict) -> None:
        endpoint_model = metadata.get(MetadataEnum.MODEL_KEY)
        if self._get_query_params(endpoint):
            query_parameters = (
                [
                    self._create_parameter_definition(
                        arg, MetadataEnum.PARAM_QUERY_TYPE)
                    for arg in self._get_query_params(endpoint)
                ])
            parameters.extend(query_parameters)

        if metadata.get(MetadataEnum.MODEL_KEY):
            method_definition[DefinitionEnum.REQUEST_BODY] = (
                self._get_model_reference(endpoint=endpoint))

            self._add_component(
                name=endpoint.component_key,
                model=self._get_model_component_schema(
                    model=endpoint_model))

    def _get_base_definition(self) -> dict:
        return {
            'openapi': DefinitionEnum.OPEN_API_VERSION,
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
        return {
            '200': {
                'description': 'Success'
            }
        }

    def _get_model_reference(self, endpoint: Endpoint) -> Union[dict, None]:
        if (self._metadata.get_endpoint_metadata(endpoint.metadata_key)
                and self._metadata.get_endpoint_metadata(endpoint.metadata_key).get(
                    MetadataEnum.MODEL_KEY)):

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
                endpoint.metadata_key).get(MetadataEnum.QUERY_PARAM_KEY)

            if query_parameters:
                return query_parameters
