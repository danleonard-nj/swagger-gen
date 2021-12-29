from swagger_gen.lib.exceptions import NullReferenceException
from swagger_gen.lib.endpoint import Endpoint
from swagger_gen.lib.schema import SwaggerDefinition
from typing import List
from flask import Flask


class Builder:
    def __init__(self, app: Flask, app_name: str, app_version: str):
        if not app:
            raise NullReferenceException('app')

        self._app = app
        self._definition = SwaggerDefinition(
            app_name=app_name,
            app_version=app_version)

    def build_definition(self) -> dict:
        endpoints = self._get_swagger_endpoints()

        for endpoint in endpoints:
            self._definition.add_endpoint(endpoint)

        return self._definition.get_definition()

    def _get_swagger_endpoints(self) -> List[Endpoint]:
        # TODO: Feature to define custom exclusions

        endpoints = []
        for rule in self._app.url_map.iter_rules():
            if not any([x for x in ['swagger', 'static'] if x in rule.rule]):
                endpoint = Endpoint(
                    rule=rule)
                endpoints.append(endpoint)
        return endpoints
