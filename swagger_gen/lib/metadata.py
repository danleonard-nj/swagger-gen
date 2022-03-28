from functools import wraps
from importlib.metadata import metadata
from typing import Callable, Iterable, List, Union

from numpy import isin
from swagger_gen.lib.endpoint import SwaggerEndpoint
from swagger_gen.lib.logger import get_logger
from swagger_gen.lib.utils import not_null

logger = get_logger()


class EndpointMetadata:
    def __init__(self, view_function, metadata):
        self.function_key = view_function.__name__
        self._validate_metadata_params(metadata)
        self.metadata = metadata

    @property
    def summary(self) -> Union[str, bool]:
        ''' Displayed next to the route in the collapsed endpoint on the UI'''
        return self.metadata.get('summary') or False

    @property
    def description(self) -> Union[str, bool]:
        ''' Longer endpoint description displayed in the expanded endpoint on the UI  '''
        return self.metadata.get('description') or False

    @property
    def query_params(self) -> Union[List[str], bool]:
        ''' Optional query parameter definitions '''
        return self.metadata.get('query_params') or False

    @property
    def response_model(self) -> Union[tuple, Iterable[tuple]]:
        '''Sample response model'''
        return self.metadata.get('response_model') or False

    @property
    def request_model(self) -> dict:
        '''Sample request model'''
        return self.metadata.get('request_model') or False

    @property
    def is_deprecated(self) -> dict:
        '''Deprecated flag'''
        return self.metadata.get('is_deprecated') or False

    @property
    def security(self) -> dict:
        '''The security scheme on the endpoint (links by key to the component)'''
        return self.metadata.get('security') or False

    @property
    def scopes(self) -> dict:
        '''Scopes for OAuth security scheme'''
        return self.metadata.get('scopes') or False

    def _validate_metadata_params(self, metadata: dict) -> None:
        meta_keys = [
            'query_params',
            'summary',
            'description',
            'response',
            'blueprint',
            'request_model',
            'response_model',
            'security',
            'scopes']

        invalid_keys = [
            x for x in metadata.keys()
            if x not in meta_keys]

        if len(invalid_keys) > 0:
            invalid_params = ', '.join(invalid_keys)
            raise Exception(
                f'Invalid Swagger metadata parameter(s): {invalid_params}')


class MetadataCollection:
    def __init__(self):
        self._metadata = dict()

    def __getitem__(self, view_function_name: Union[Callable, str]) -> EndpointMetadata:
        ''' Return the endpoint metadata at the given key (name of the view function) '''
        return self._metadata.get(view_function_name)

    def __setitem__(self, view_function_name: Union[Callable, str], endpoint_metadata: EndpointMetadata):
        not_null(view_function_name, 'view_function_name')
        not_null(endpoint_metadata, 'endpoint_metadata')

        if view_function_name in self._metadata:
            raise Exception(f"""A view function with the name {view_function_name} already has metadata 
            defined.  If you are using a Blueprint, either pass the instance as 'blueprint' on @swagger_metadata
            or enable 'implicit_blueprints' if your app does not contain multiple blueprints in a single context""")

        self._metadata[view_function_name] = endpoint_metadata
