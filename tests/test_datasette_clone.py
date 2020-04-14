from click.testing import CliRunner
from datasette_clone import cli
import json
import os
import pytest

DATABASES = [{"path": "fixtures.db", "hash": "1234", "is_mutable": False}]


def setup_mocks(requests_mock):
    requests_mock.get(
        "https://latest.datasette.io/-/databases.json", json=DATABASES,
    )
    requests_mock.get("https://latest.datasette.io/fixtures.db", text="fixtures!")


def test_datasette_clone(requests_mock):
    setup_mocks(requests_mock)
    runner = CliRunner()
    with runner.isolated_filesystem():
        assert [] == os.listdir(".")
        result = runner.invoke(cli.cli, ["https://latest.datasette.io/"])
        assert result.exit_code == 0
        assert ["fixtures.db", "databases.json"] == os.listdir(".")
    first, second = requests_mock.request_history
    assert "https://latest.datasette.io/-/databases.json" == first.url
    assert "https://latest.datasette.io/fixtures.db" == second.url


@pytest.mark.parametrize("change_hash", [False, True])
def test_datasette_clone_skips_download_if_hash_matches(requests_mock, change_hash):
    setup_mocks(requests_mock)
    runner = CliRunner()
    with runner.isolated_filesystem():
        databases_on_disk = DATABASES
        if change_hash:
            databases_on_disk = [dict(DATABASES[0], hash="changed")]
        open("databases.json", "w").write(json.dumps(databases_on_disk))
        result = runner.invoke(cli.cli, ["https://latest.datasette.io/"])
        assert result.exit_code == 0
    if change_hash:
        assert 2 == len(requests_mock.request_history)
    else:
        # Should only have made one request
        assert 1 == len(requests_mock.request_history)
    assert (
        "https://latest.datasette.io/-/databases.json"
        == requests_mock.request_history[0].url
    )
