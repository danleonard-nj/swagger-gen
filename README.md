# swagger-gen
Plug and play Swagger UI documentation generator for Flask.

Much like the *awesome* `Swashbuckle.AspNetCore.SwaggerGen`, Flask needs a user-friendly, no-nonsense Swagger generation library that doesn't turn your service code into spaghetti.  Inspired by Swashbuckle, `swagger-gen` comes packaged with all the necessary dependencies (HTML, CSS, React JS and modules, etc) to run Swagger UI with no modifications to the Flask application required to serve them and generate a beautiful Swagger page for your Flask app.

## Quickstart


## Dependencies
The web content required to display Swagger UI is packaged in a binary and included as a package resource.  On configuration, the dependencies are fetched from the package and hooked into the Flask app route definitions, so Flask will serve those static dependencies without requiring them to exist in app space.  Serving static files from the Flask web server, for almost any other reason, is not a great choice.  However, unless you're worried about heavy load on your Swagger page (if that's the case, you may have a different problem to worry about) it won't be an issue.

## Basic Configuration

At the most basic, without any additional metadata defined on the routes, `swagger-gen` will generate a Swagger UI with the route names, segments and methods.  The basic configuration is confined to a few parameters on the `Swagger` class:

```python
swagger = Swagger(
    app=app,
    title='azure-gateway',
)

swagger.configure()
```

This is enough to get a page up and running!  Currently, there is no support for version delineation on the routes, although it's certainly a good candidate for future improvements.

## `@swagger_metadata` usage

```python
@swagger_metadata(
    request_model={'message' : 'string'},
    summary='An example route',
    description='This is an example route, check it out!',
    response_model=[(200, 'Success'), (500, 'Error')],
    query_params=['first_name', 'last_name'],
    security='bearer')
@app.route('/api/test')
def post_query(methods=['POST']):
    return something
```

## Endpoint Metadata

There are a few things that make generating comprehensive specs interesting with Flask compared to other stacks that have similar packages:

* We don't have a concept of a request and response model, as opposed to a framework like .NET where these things are defined, and samples can be generated from them.
* We also don't explicitly define query parameters, they're parsed at runtime from the request context
* We also don't have response definitions, like what status codes we might return

What we do have:
* The route and any interpolated route segments
* The request methods accepted by the route
* Obviously, we've got the endpoint itself

To include these, other Swagger packages have typically relied on a manual spec file being referenced somewhere, which may be okay in some cases but probably frustrating for most.  In the interest of keeping things clean, the duty of collecting route metadata happens in two places.

First is what's been described, the buildup using `app` and stealing the required data from the route map.  The second part is handled through route decorators, and occurs *before the `app` instance is available.*  The decorators run on import, and store the parameters for that route in a global collection.  These are totally detatched from the actual routes that are parsed on buildup, and it is the `view_function` name that links them back.

### What about blueprints?

Route method (view function) names when hooked in to the flask app directly (`@app.route`) must be unique, which is good because we're using that function name as a key to link the metadata and the route data from the decorators and buildup respectively.  But a `Blueprint` does not require cardinality for the view functions.  This is because behind the scenes, Flask is actually storing that view function with the blueprint name as a prefix, i.e. the route `get_thing` on blueprint `thing_bp` is stored at key `thing_bp.get_thing`.

**gasp**

This is a problem if we have two routes defined across different blueprints with the same name, because we'll be overwriting the previous route's metadata if we only use the function name.  Since we're collecting this stuff of the route before we have access to the Flask `app` (before it even exists) we need a way to uniquely identify these on both sides, but we only have access to the view function itself when we need to generate a key to do that, which is a problem.

There are two options to handle this, both require having access to the `Blueprint` instance:
* The instance can be passed in as a parameter to the decorator, and we'll store that view function with the blueprint prefix, the same way Flask will during the buildup.
* **If you keep your blueprints in separate files** meaning you don't have more than a single blueprint defined in a single module, it can be parsed implicitly and the instance doesn't need to be passed to `@swagger_metadata`.  This is done by fetching the caller stack frame (which is the module that contains the decorated route methods) and pulling the `Blueprint` instance from the locals in that context.  If you are working with multiple blueprints in a single file, there is no way to know which blueprint belongs to which view function, so the `Blueprint` needs to be passed in explicitly.  If `implicit_blueprints` is enabled and more than one `Blueprint` instances are found in the caller context, the app will throw an exception.

The full list of available metadata options is availabe in the decorator doc string.  There are also additional values on the `Swagger` constructor that map to additional optional fields on the spec.

Want to contribute?  Have an issue?
https://github.com/danleonard-nj/swagger-gen