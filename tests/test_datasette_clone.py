from click.testing import CliRunner
from datasette_clone import cli
import os


def test_datasette_clone(requests_mock):
    requests_mock.get(
        "https://latest.datasette.io/-/databases.json",
        json=[{"path": "fixtures.db", "hash": "1234", "is_mutable": False}],
    )
    requests_mock.get("https://latest.datasette.io/fixtures.db", text="fixtures!")
    runner = CliRunner()
    with runner.isolated_filesystem():
        assert [] == os.listdir(".")
        result = runner.invoke(cli.cli, ["https://latest.datasette.io/"])
        assert result.exit_code == 0
        assert ["fixtures.db", "databases.json"] == os.listdir(".")
    first, second = requests_mock.request_history
    assert "https://latest.datasette.io/-/databases.json" == first.url
    assert "https://latest.datasette.io/fixtures.db" == second.url
