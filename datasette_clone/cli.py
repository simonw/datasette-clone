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
    if not datasette_url.startswith("https://") and not datasette_url.startswith(
        "https://"
    ):
        # It's 2020, if you want http you'll have to be explicit about it
        datasette_url = "https://{}".format(datasette_url)
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
            click.echo(
                "Found existing {}, cached databases are:".format(directory_json)
            )
            click.echo(json.dumps(cached_databases, indent=4))

    for path, hash in databases_to_fetch.items():
        db_path = directory / path
        if cached_databases.get(path) != hash:
            if verbose:
                click.echo(
                    "Fetching {}, current hash {} != {}".format(
                        db_path, hash, cached_databases.get(path)
                    )
                )
            # Fetch it!
            response = requests.get(base_url + path, headers=headers, stream=True)
            with open(db_path, "wb") as fd:
                if verbose and "content-length" in response.headers:
                    with click.progressbar(
                        length=int(response.headers["content-length"]),
                        label="{:,.2f} MB".format(float(response.headers["content-length"]) / (1024 * 1024))
                    ) as bar:
                        for chunk in response.iter_content(chunk_size=1024 * 10):
                            bar.update(len(chunk))
                            fd.write(chunk)
                else:
                    for chunk in response.iter_content(chunk_size=1024 * 10):
                        fd.write(chunk)
        else:
            if verbose:
                click.echo("Skipping {}, hash has not changed".format(db_path))

    # Last step: grab a copy of the metadata
    metadata_json = directory / "metadata.json"
    metadata_json.open("w").write(
        json.dumps(
            requests.get(base_url + "-/metadata.json", headers=headers).json(), indent=4
        )
    )
    directory_json.open("w").write(json.dumps(databases, indent=4) + "\n")
    if verbose:
        click.echo("Wrote {}".format(directory_json))
        click.echo("Wrote {}".format(metadata_json))
