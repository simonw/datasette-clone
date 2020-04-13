# datasette-clone

[![PyPI](https://img.shields.io/pypi/v/datasette-clone.svg)](https://pypi.org/project/datasette-clone/)
[![CircleCI](https://circleci.com/gh/simonw/datasette-clone.svg?style=svg)](https://circleci.com/gh/simonw/datasette-clone)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-clone/blob/master/LICENSE)

Create a local copy of database files from a Datasette instance.

## How to install

    $ pip install datasette-clone

## Usage

This only works against Datasette instances running immutable databases (with the `-i` option). Databases published using the `datasette publish` command should be compatible with this tool.

To download copies of all `.db` files from an instance, run:

    datasette-clone https://latest.datasette.io

You can provide an optional second argument to specify a directory:

    datasette-clone https://latest.datasette.io /tmp/here-please

The command stores its own copy of a `databases.json` manifest and uses it to only download databeses that have changed.

If your instance is protected by an API token, you can use `--token` to provide it:

    datasette-clone https://latest.datasette.io --token=xyz

For verbose output showing what the tool is doing, use `-v`.
