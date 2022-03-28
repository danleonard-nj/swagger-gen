from swagger_gen.lib.dependency import DependencyProvider
from swagger_gen.lib.endpoint import SwaggerEndpoint
from swagger_gen.lib.schema import SwaggerDefinition
from swagger_gen.lib.utils import is_type, not_null
from typing import List
from flask import Flask


class Swagger:
    '''
    Swagger-gen automated documentation generator:

    Out of the box, with only the required parameters defined, a basic Swagger UI
    page will be generated containing the route information that is available to
    Flask without additional metadata.  This includes:

    * Route name
    * Route method
    * Route segments as parameters

    Additional metadata can be defined via the `swagger_metadata` decorator on the
    route itself.

    params:
    `app` :   the Flask app

    spec params:

    header:
    `title` : the title, displayed at the head of the page
    `version` : the application version
    `description`: the description, displayed under the title
    `contact_email`: the email address to display in the contact section

    license:
    `license_name`: name of the license to display in the license section
    `license_url`: link to the license docs, displayed in license section

    security:
    `auth_schemes`: list of security schemes

    Currently, route-specific versions are not supported, but are slated as a
    priority for future releases
    '''

    def __init__(
            self,
            app: Flask,
            **kwargs):

        # app_name: str = None,
        # app_version: str = 'v1',
        # url: str = '/swagger'):

        not_null(app, 'app')
        is_type(app, 'app', Flask)

        self._app: Flask = app

        # Swagger UI index endpoint
        self._url = kwargs.get('url') or '/swagger'
        is_type(self._url, 'url', str, null=False)

        self._definition: SwaggerDefinition = SwaggerDefinition(
            app=app,
            **kwargs)

    def configure(self):
        '''
        Configure swagger-gen.

        A Swagger UI definition file is generated from the defined endpoints
        in the Flask app.  The `werkzeug` `Rule` class in the route mapping is
        used to generate the endpoint specs.  No explicit configuration is
        required, the documentation will be generated automatically. Optionally, 
        view functions can be decorated with the `@swagger_metadata` decorator 
        to define additional endpoint features like query parameters and request 
        body models.  The Swagger UI will be hosted at `/swagger/index.html` by 
        default, but this can be overridden via the `url` parameter in the 
        constructor. The dependencies for the Swagger UI page are loaded from 
        package resources and served up from memory.  The dependencies are added 
        as routes to the app automatically.        
        '''

        # Configure the Swagger dependency route (to serve css/js files from memory)
        _resources: DependencyProvider = DependencyProvider(
            app=self._app,
            url=self._url)
        _resources.bind_dependency_routes()

        # Build the Swagger spec document
        definition = self._build_swagger_definitions()

        #
        self._bind_schema_endpoint(
            definitions=definition)

    def _bind_schema_endpoint(self, definitions: dict) -> None:
        '''
        Bind the swagger configuration file route

        params:
        schema  :   the swagger configuration file
        '''

        not_null(definitions, 'definitions')

        # Flask view function that will return the Swagger definition
        def get_schema():
            return definitions

        self._app.add_url_rule(
            rule='/swagger/v1/swagger.json',
            view_func=get_schema,
            methods=['GET'])

    def _build_swagger_definitions(self) -> dict:
        '''
        Build the Swagger JSON definitions
        '''

        # Get the Flask endpoints to generate the documentation from
        endpoints = self._get_swagger_endpoints()

        # Generate the endpoint documentation
        for endpoint in endpoints:
            self._definition.add_endpoint(endpoint)

        return self._definition.get_definition()

    def _get_swagger_endpoints(self, exclude_routes: List[str] = None) -> List[SwaggerEndpoint]:
        '''
        Parse the endpoints from the `werkzeug` `Rule` definitions
        in the Flask app
        '''

        # TODO Feature to define custom exclusions

        # Default keys to exclude from list of endpoints to generate definitions
        exclusion_keys = ['swagger', 'static']

        # Allow addition route exclusions if required.  Anything specified here
        # will not be displayed in the documentation
        if (exclude_routes is not None
            and isinstance(exclude_routes, list)
                and len(exclude_routes) > 0):
            exclusion_keys.extend(exclude_routes)

        endpoints = []

        # Fetch the endpoints from the mapped rules in the Flask app
        for rule in self._app.url_map.iter_rules():
            # If the endpoint is not in the list of excluded routes
            if not any([x for x in ['swagger', 'static'] if x in rule.rule]):
                endpoint = SwaggerEndpoint(
                    rule=rule)
                endpoints.append(endpoint)

        return endpoints
