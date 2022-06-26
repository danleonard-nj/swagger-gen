from swagger_gen.lib.utils import (
    element_at,
    not_null
)
from swagger_gen.lib.constants import Method
from werkzeug.routing import Rule
from typing import List


class SwaggerEndpoint:
    def __init__(self, rule: Rule):
        not_null(rule, 'rule')
        self._rule = rule

    @property
    def view_function_name(self):
        ''' The name of the method that defines the route '''
        return self._rule.endpoint

    @property
    def methods(self):
        ''' The allowed methods on the route '''
        return self._get_methods()

    @property
    def component_key(self) -> str:
        '''Key linking the path and the component in the spec'''
        return self._get_view_name()

    @property
    def endpoint_literal(self) -> str:
        ''' The endpoint name to display on the Swagger page '''
        return self._format_route_literal()

    @property
    def segment_params(self):
        '''URL segment parameters'''
        return self._rule.arguments

    @property
    def tag(self):
        ''' The section name that groups the endpoints in the Swagger UI '''
        return self._get_endpoint_tag()

    def _get_view_name(self) -> str:
        '''Get the formatted view name, removing blueprint prefixes'''

        not_null(self._rule.endpoint, 'endpoint')

        segments = self._rule.endpoint.split('.')
        if len(segments) > 1:
            return segments[1]
        return self._rule.endpoint

    def _get_endpoint_tag(self) -> str:
        '''
        Get the endpoint tag.  The tag becomes the title of the group of 
        endpoints sharing a common base path.

        When generating documentation dynamically from the app routes, 
        the only thing we have to go with w/r/t grouping endpoints together 
        is the base segment of the URL.  As a result, if the base segment 
        is the same for every endpoint, they'll all be grouped under one
        section.  A common scenario is an /api prefix on the route.  So to
        avoid this (specific scenario) we'll strip off the /api prefix if
        it exists

        TODO: Expose a parameter on `swagger_metadata` to pass in a specific
        tag in the event we want to override the automatic tag for something
        more specific, etc
        '''

        endpoint_segments = self._rule.rule.split('/')

        tag_position = 1
        if element_at(endpoint_segments, 1) == 'api':
            tag_position = 2

        # Get the tag segment from the index of the segment list
        endpoint_tag = element_at(
            _iterable=endpoint_segments,
            index=tag_position)

        if not endpoint_tag:
            raise Exception(
                f'Failed to parse tag from endpoint: {self._rule.rule}')

        return endpoint_tag

    def _format_route_literal(self) -> str:
        '''
        Swap carets for curly braces in the endpoint parameters.  The Flask
        routes require route segments to be enclosed in carats.  In order for
        Swagger UI to handle the segments, they need to be enclosed in curly
        braces

        Flask: `<order_id`>
        Swagger: `{order_id}`
        '''

        route = self._rule.rule

        not_null(route, 'route')

        if '<' in route:
            route = (route.replace(
                '<', '{').replace(
                    '>', '}')
            )
        return route

    def _get_methods(self) -> List[str]:
        '''Get display methods, ignoring OPTIONS and HEAD'''

        return ([
            method for method in self._rule.methods
            if method not in [
                Method.OPTIONS,
                Method.HEAD]
        ])
