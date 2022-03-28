
from functools import wraps
import inspect
import logging
from typing import Callable
from swagger_gen.lib.metadata import EndpointMetadata, MetadataCollection
from swagger_gen.lib.utils import element_at, defined, is_type, not_null
from flask import Blueprint
from inspect import FrameInfo

logger = logging.getLogger(__name__)
endpoint_metadata = MetadataCollection()


def get_blueprint_from_context():
    ''' 
    Implicitly find the Blueprint (if there is one) that the view function is hooked into

    Why do?
        When the view functions are registered in the Flask app, there's actually a prefix on
    routes defined by a Blueprint under the hood.  This allows the same method name to exist
    on multiple blueprints without overwriting the previous view functions with the same name.

    Important note on the metadata decorator: we have to assume we're running before the app
    even exists. 

    Why this matters?
        This means we don't have the luxury of copying Flask's homework and just using the names
    of the view functions it generates (which would have the blueprint prefix) so we imitate it.

    We'll infer the view function name (based on the __name__ of the view function we're passed
    in the decorator, which is the parent function) and try to find a blueprint in the context one
    frame above the decorator, which will be the source file where the route is declared.  From
    there, we'll have access to the __name__ attribute on the blueprint, and can generate an
    accurate key to store the route metadata.  From there, when the Flask app is created and the
    Swagger buldup starts, we'll be able to lookup the routes as they're hooked into the Flask 
    app to see if we've squirreled away any metadata for it.  Simple enough, right?
    '''

    # Fetch the stack frame second from the top if we can
    frames = inspect.stack()
    caller_frame = element_at(inspect.stack(), 2)

    # Short out and return null if we can't for some reason
    if not caller_frame:
        return None

    # Fetch the locals from the caller stack frame.  In order to register the routes on a Blueprint
    # with the route decorator the Blueprint instance has to be in that scope.  Since the metadata
    # decorator will sit on top of the route decorator, we can take a stab at trying to find the blueprint
    # it's tied to implicitly.  Since we don't have access to the blueprint through the view function
    # (right? not that I could find, anyway) have to get a little hacky.  The blueprint instance can also
    # be passed in to the metadata decorator explicitly as well.
    caller_locals = caller_frame.frame.f_locals

    # Iterate through the caller function locals until we find the blueprint.  Since we don't know the
    # actual name of the variable, we're looking for the type.  If there are multiple blueprints defined
    # or imported into a single file, we'll throw an exception and require the Blueprint instance be passed
    # explicitly.

    blueprints = list()
    for _, instance in caller_locals.items():
        if isinstance(instance, Blueprint):
            blueprints.append(instance)

    # Multiple blueprints aren't welcome here
    if len(blueprints) > 1:
        raise Exception(f'''
            Implicit blueprint parsing cannot be used if multiple blueprints exist in the caller context.
            If a single source file contains routes that refer to multiple blueprint instances, or there are
            multiple blueprints imported into the caller context, there's no way to know which one belongs to
            which route!  Try splitting the blueprints out into individual source files or passing them to the
            metadata decorator explicitly''')

    # No blueprints found in the context
    if not any(blueprints):
        return None

    blueprint = element_at(blueprints, 0)
    return blueprint.name


def get_blueprint_view_name(blueprint: Blueprint, view_function: Callable):
    '''
    Get the full view function name from the blueprint and the
    view function

    Ex: for a blueprint named `test` and a view function `post`
    the full name `test.post`

    params:
    `blueprint`: instance of a `Blueprint`
    `view_function`: the Flask view function
    '''
    return '.'.join([
        blueprint.name,
        view_function.__name__])


def swagger_metadata(**kwargs):
    '''
    Defines optional metadata on the route to be displayed in the
    generated Swagger UI documentation

    params:
    `summary`: the endpoint summary, displayed on the collapsed
    route.

    `description`: the route description, displayed when the route
     is expanded.

    `query_params`: the query params for the endpoint.  These are
    displayed as parameters in the expanded endpoint.  Required or
    optional specs are not currently supported, but are a priority
    for future releases.

    `request_model`: the route model definition.  This is both displayed
    as a component at the footer of the page, and on the endpoint
    it's defined on.  It should be key-value pairs containing the
    field name and the type in the shape of the expected request.

    `response_model`: an example of the endpoint response model

    `implicit_blueprints`: default is False, if enabled, we'll try
    to infer the blueprint the route is on (if it exists) by the
    function caller local context.  If more then one blueprint is
    defined or imported in the local context of the function caller,
    blueprints must be defined explicitly

    `blueprint`: the blueprint the route belongs to, this is used
    to create the key to store the route metedata that matches the
    name of the view function when it's created by the Flask app

        Ex: ```{'username': 'string', 'userId': 'int'}```
    '''
    def inner(view_function: Callable) -> Callable:
        ''' Flask view function passed in '''

        # Parameters
        _summary = kwargs.get('summary')
        is_type(_summary, 'summary', str)

        _description = kwargs.get('description')
        is_type(_description, 'description', str)

        _query_params = kwargs.get('query_params')
        is_type(_query_params, 'query_params', list)

        _request_model = kwargs.get('request_model')
        is_type(_request_model, 'request_model', (dict, list))

        _response_model = _request_model = kwargs.get('response_model')
        is_type(_response_model, 'response_model', list)

        _implicit_blueprints = kwargs.get('implicit_blueprints')
        is_type(_implicit_blueprints, 'implicit_blueprints', bool)

        _blueprint = kwargs.get('blueprint')
        is_type(_blueprint, 'blueprint', Blueprint)

        if defined(_blueprint) and _implicit_blueprints is True:
            raise Exception(
                f'Implicit blueprints cannot be used when a Blueprint is passed explicitly')

        _has_blueprint = False

        # Blueprint defined explicitly
        if defined(_blueprint):
            _has_blueprint = True
            _blueprint = _blueprint.name

        # Find blueprints implicitly
        if _implicit_blueprints is True:
            _has_blueprint = True
            _blueprint = get_blueprint_from_context()

        _endpoint_metadata = EndpointMetadata(
            view_function=view_function,
            metadata=kwargs)

        # If the route is defined on a blueprint, we need to add the blueprint name
        # to the key that we store the metadata at.  The same method name can occur
        # in two different blueprints, so simply using the view function name won't
        # suffice here
        if _has_blueprint:
            blueprint_key = f'{_blueprint}.{view_function.__name__}'
            endpoint_metadata[blueprint_key] = _endpoint_metadata
        else:
            # If it's not a blueprint route, store the endpoint metadata at the view
            # function name
            endpoint_metadata[view_function.__name__] = _endpoint_metadata

        @wraps(view_function)
        def wrapper(*_args, **_kwargs):
            return view_function(*_args, **_kwargs)
        return wrapper
    return inner


# TODO: This should be moved to swagger_metadata

def swagger_response(status_code, description):
    '''
    Docs
    '''
    def real_decorator(view_function):
        response = format_response(
            status_code=status_code,
            description=description)

        if not endpoint_metadata[view_function]:
            endpoint_metadata[view_function] = EndpointMetadata(
                view_function=view_function,
                metadata={'response': response})

        else:
            _meta = endpoint_metadata[view_function]
            if not _meta.get('responses'):
                _meta['responses'] = [response]
            else:
                _meta['responses'].append(response)

        @wraps(view_function)
        def wrapper(*_args, **_kwargs):
            return view_function(*_args, **_kwargs)
        return wrapper
    return real_decorator


def get_endpoint_metadata(view_function_name) -> dict:
    '''Get the endpoint metadata by the view funtion name key'''

    not_null(view_function_name, 'view_function_name')
    return endpoint_metadata[view_function_name]
