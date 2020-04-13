import click
import json
import pathlib
import requests
from urllib.parse import urlparse


@click.command()
@click.argument("datasette_url")
@click.argument(
    "directory", type=click.Path(file_okay=False, dir_okay=True), default="."
)
@click.option(
    "--token", help="Optional API token to use when talking to Datasette",
)
@click.option(
    "-v", "--verbose", is_flag=True, help="Verbose output",
)
def cli(datasette_url, directory, token, verbose):
    "Create a local copy of database files from a Datasette instance"
    bits = urlparse(datasette_url)
    directory = pathlib.Path(directory)
    if not directory.exists():
        directory.mkdir(parents=True)
    base_url = "{}://{}/".format(bits.scheme, bits.netloc)
    databases_url = "{}-/databases.json".format(base_url)
    headers = {}
    if token:
        headers["Authorization"] = "Bearer {}".format(token)
    response = requests.get(databases_url, headers=headers, allow_redirects=False)
    if response.status_code != 200:
        raise click.ClickException("Could not access {}".format(databases_url))
    databases = response.json()
    databases_to_fetch = {
        db["path"]: db["hash"]
        for db in databases
        if not db["is_mutable"] and db["hash"] is not None
    }
    # Do we have a previously cached databases.json ?
    cached_databases = {}
    directory_json = directory / "databases.json"
    if directory_json.exists():
        cached_databases = {
            db["path"]: db["hash"]
            for db in json.load(directory_json.open())
            if not db["is_mutable"] and db["hash"] is not None
        }
        if verbose:
            click.echo("Found existing databases.json, cached databases are:")
            click.echo(json.dumps(cached_databases, indent=4))

    for path, hash in databases_to_fetch.items():
        if cached_databases.get(path) != hash:
            if verbose:
                click.echo(
                    "Fetching {}, current hash {} != {}".format(
                        path, hash, cached_databases.get(path)
                    )
                )
            # Fetch it!
            r = requests.get(base_url + path, headers=headers)
            with open(directory / path, "wb") as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
        else:
            if verbose:
                click.echo("Skipping {}, hash has not changed".format(path))

    directory_json.open("w").write(json.dumps(databases, indent=4) + "\n")
