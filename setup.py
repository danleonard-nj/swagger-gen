from setuptools import setup, find_packages

VERSION = '0.1.0'
DESCRIPTION = 'Swagger UI for Flask apps'
LONG_DESCRIPTION = 'Automatically generate Swagger UI documentation for a Flask app.  Batteries included.'

setup(
    name="swagger-gen",
    version=VERSION,
    author="Dan Leonard",
    author_email="dcl525@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    package_data={'swagger_gen': ['./resources/swagger.pkl']},
    packages=find_packages(),
    install_requires=['flask'],
    keywords=['python', 'swagger-gen'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
