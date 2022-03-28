from swagger_gen.lib.utils import element_at, not_null
from swagger_gen.lib.constants import (
    ContentType,
    DependencyInfo,
    Method
)
from werkzeug.exceptions import abort
from flask import Flask, Response
import importlib.resources
import pickle

mimetype_mapping = {
    'css': ContentType.TEXT_CSS,
    'js': ContentType.JAVASCRIPT
}


class DependencyProvider:
    '''
    The Swagger web dependencies (js, css, html, etc) are hooked into Flask explicitly
    as routes and the dependencies themselves are serverd from memory.  They're stored
    in a pickle file in the package resources.  This is in an effort to keep the package
    small and easy to install and use, as opposed to having to download the files, stage
    them in a static directory, etc
    '''

    def __init__(self, app: Flask, url: str):
        not_null(app, 'app')
        not_null(url, 'url')

        self._app = app
        self._url = url
        self._resources = self._load_resources()

    def _load_resources(self) -> dict:
        '''Load Swagger dependencies to memory'''

        try:
            # Loading the pickled Swagger UI JS, CSS and HTML files from
            # the module source directory
            data = importlib.resources.open_binary(
                DependencyInfo.PKG_RESOURCE_MODULE,
                DependencyInfo.PKG_SWAGGER)

            return pickle.load(data)
        except Exception as ex:
            raise Exception(f'Failed to load Swagger dependencies: {str(ex)}')

    def _get_resource_type(self, resource_name: str) -> str:
        ''' 
        Get the resource file extension from the resource name

        `resource_name`: the name of the resource file, i.e. `swagger.js`
        '''

        not_null(resource_name, 'resource_name')
        return element_at(resource_name.split('.'), -1)

    def _get_resource(self, resource_name: str):
        '''
        The view function to fetch the dependency resource.  This is registered
        on the Flask app and dynamically serves the dependencies from a single
        registered route.  

        The view function is registered at `/swagger/<resource_name>`, so when
        the browser requests any of the static Swagger dependencies, the name of
        the resource is passed in as `resource_name`.  That name as a key is used 
        to fetch the actual resource content, and it's returned as a response.

        This means we're service static files from the Flask web server, which in
        almost all cases is a recipe for a slow app, but the exception is made in
        this case because the files are served directly from memory and the page
        itself should never see enough traffic for it to matter.

        #TODO: Consider alternative methods for serving dependencies if memory is
        # not appropriate for a scenario?
        '''

        resource = self._resources.get(resource_name)
        if not resource:
            abort(404)

        # Get the correct file mimetype to serve it to the browser.  The two
        # types that we're concerned with here are text/css and text/javascript
        mimetype = mimetype_mapping.get(
            self._get_resource_type(resource_name))

        # If there is a matching mimetype, return the resource with that, otherwise
        # return the resouce as-is
        if mimetype:
            return Response(
                resource,
                mimetype=mimetype)

        return resource

    def bind_dependency_routes(self) -> None:
        '''
        Bind all required Swagger dependency routes.  The  dependencies 
        defined in swagger.pkl will get served from memory via the rules 
        defined
        '''

        # Register the resourceroute to serve the page dependencies requested
        # by Swagger UI
        self._app.add_url_rule(
            rule='/swagger/<resource_name>',
            view_func=self._get_resource,
            methods=[Method.GET])

        def get_index():
            return Response(
                self._resources.get('index.html'))

        # Bind the Swagger UI index at the default route '/swagger' or
        # the optional route specified in the main class constructor
        index_path = self._url or '/swagger/index.html'

        # Bind the view function that will serve index.html
        self._app.add_url_rule(
            rule=index_path,
            view_func=get_index,
            methods=[Method.GET])
