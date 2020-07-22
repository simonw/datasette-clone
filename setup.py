from setuptools import setup
import os

VERSION = "0.5"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-clone",
    description="Create a local copy of database files from a Datasette instance",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-clone",
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["datasette_clone"],
    entry_points="""
        [console_scripts]
        datasette-clone=datasette_clone.cli:cli
    """,
    install_requires=["requests", "click"],
    extras_require={"test": ["pytest", "requests-mock"]},
    tests_require=["datasette-auth-github[test]"],
)
