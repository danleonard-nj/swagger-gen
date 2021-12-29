from swagger_gen.lib.constants import JwtScheme


class Security:
    def _generate_jwt_security_scheme_definition(self, scheme_name: JwtScheme = JwtScheme.SCHEME):
        swagger_security[scheme_name] = {
            'type': JwtScheme.TYPE,
            'description': JwtScheme.DESCRIPTION,
            'scheme': JwtScheme.SCHEME,
            'bearerFormat': JwtScheme.FORMAT
        }
