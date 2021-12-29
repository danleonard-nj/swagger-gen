from swagger_gen.lib.builder import Builder
from swagger_gen.lib.dependency import DependencyProvider
from swagger_gen.lib.exceptions import NullReferenceException
from swagger_gen.lib.builder import Builder
from flask import Flask


class Swagger:
    def __init__(self, app: Flask, app_name: str = None, app_version: str = None, url: str = None):
        if not app:
            raise NullReferenceException('app')

        self._app: Flask = app
        self._app_name: str = app_name or app.__name__
        self._app_version: str = app_version or 'v1'
        self._url = url

        self._builder = Builder(
            app=app,
            app_name=app_name,
            app_version=app_version)

    def configure(self):
        '''
        Configure swagger-gen.

        A Swagger UI definition file is generated from the defined endpoints
        in the Flask app.  The werkzeug.Rule class in the route mapping is
        used to generate the endpoint specs.  No explicit configuration is
        required, the documentation will be generated automatically. Optionally, 
        view functions can be decorated with the @swagger_metadata  decorator 
        to define additional endpoint features like query parameters and request 
        body models.  The Swagger UI will be hosted at /swagger/index.html by 
        default, but this can be overridden via the 'url' parameter in the 
        constructor. The dependencies for the Swagger UI page are loaded from 
        package resources and served up from memory.  The dependencies are added 
        as routes to the app automatically.        
        '''

        _resources = DependencyProvider(
            app=self._app,
            url=self._url)
        _resources.bind_routes()

        self._map_schema_endpoint(
            definitions=self._builder.build_definition())

    def _map_schema_endpoint(self, definitions):
        '''
        Map the swagger configuration file route

        params:
            schema  :   the swagger configuration file
        '''

        if not definitions:
            raise NullReferenceException('definitions')

        def get_schema():
            return definitions

        self._app.add_url_rule(
            rule='/swagger/v1/swagger.json',
            view_func=get_schema,
            methods=['GET'])
