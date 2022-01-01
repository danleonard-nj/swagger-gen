from swagger_gen.lib.constants import Method
from swagger_gen.lib.exceptions import NullReferenceException
from swagger_gen.lib.utils import element_at
from werkzeug.routing import Rule


class Endpoint:
    def __init__(self, rule: Rule):
        self._rule = rule

        self.endpoint = rule.rule
        self.segment_params = rule.arguments
        self.methods = self._get_methods(
            methods=rule.methods)

        self.view_name = self._get_view_name(
            view_name=rule.endpoint)
        self.tag = self._get_endpoint_tag(
            endpoint=self.endpoint)
        self.endpoint_literal = self._format_endpoint_literal(
            endpoint=self.endpoint)

        self.metadata_key = self.view_name
        self.component_key = self.view_name

    def _get_view_name(self, view_name: str) -> str:
        if not view_name:
            raise NullReferenceException('view_name')

        segments = view_name.split('.')
        if len(segments) > 1:
            return segments[1]
        return view_name

    def _get_endpoint_tag(self, endpoint) -> str:
        endpoint_segments = endpoint.split('/')

        tag_position = 1
        if element_at(endpoint_segments, 1) == 'api':
            tag_position = 2

        endpoint_tag = element_at(
            _iterable=endpoint_segments,
            index=tag_position)

        if not endpoint_tag:
            raise Exception(
                f'Failed to parse tag from endpoint: {endpoint}')

        return endpoint_tag

    def _format_endpoint_literal(self, endpoint: str):
        if not endpoint:
            raise NullReferenceException('endpoint')

        if '<' in endpoint:
            endpoint = (endpoint
                        .replace('<', '{')
                        .replace('>', '}'))
        return endpoint

    def _get_methods(self, methods):
        return ([
            method for method in methods
            if method not in [
                Method.OPTIONS,
                Method.HEAD]
        ])
