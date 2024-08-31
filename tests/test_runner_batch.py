from os import EX_OK
from pathlib import Path
from typing import Generator, TypeAlias
import pytest
from click.testing import CliRunner
from pymongo import MongoClient, errors, collection, database
from MetAromatic.models import BatchResult
from MetAromatic.runner import cli


TestData = (
    Path(__file__).resolve().parent / "resources" / "data_coronavirus_entries.txt"
)
Results: TypeAlias = collection.Collection[BatchResult]


class TestParams:
    db = "test"
    coll = "drop_me"
    coll_info = "drop_me_info"
    username = ""
    password = ""
    num_threads = 3
    num_entries = 9


def run_batch_command() -> None:
    command = (
        f"batch {TestData} --username={TestParams.username} --password={TestParams.password} "
        f"--threads=3 --database={TestParams.db} --collection={TestParams.coll}"
    )

    runner = CliRunner()
    result = runner.invoke(cli, command.split())

    if result.exit_code != EX_OK:
        pytest.fail("Batch job exited with non-zero exit code")


@pytest.fixture(scope="module")
def mongo_db() -> Generator[database.Database, None, None]:
    client: MongoClient = MongoClient(
        username=TestParams.username, password=TestParams.password
    )

    try:
        client.list_databases()
    except errors.OperationFailure as e:
        pytest.skip(str(e))
    except errors.ServerSelectionTimeoutError as e:
        pytest.exit(str(e))

    run_batch_command()
    yield client[TestParams.db]


@pytest.fixture(scope="module")
def mongo_coll(mongo_db: database.Database) -> Generator[Results, None, None]:
    yield mongo_db[TestParams.coll]
    mongo_db[TestParams.coll].drop()


@pytest.fixture(scope="module")
def mongo_coll_info(
    mongo_db: database.Database,
) -> Generator[collection.Collection, None, None]:
    yield mongo_db[TestParams.coll_info]
    mongo_db[TestParams.coll_info].drop()


def test_batch_too_few_threads(cli_runner: CliRunner) -> None:
    command = (
        f"batch {TestData} --threads=-1 "
        f"--database={TestParams.db} --collection={TestParams.coll}"
    )

    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code != EX_OK


def test_batch_too_many_threads(cli_runner: CliRunner) -> None:
    command = (
        f"batch {TestData} --threads=100 "
        f"--database={TestParams.db} --collection={TestParams.coll}"
    )

    result = cli_runner.invoke(cli, command.split())
    assert result.exit_code != EX_OK


def test_correct_count(mongo_coll: Results) -> None:
    assert len(list(mongo_coll.find())) == TestParams.num_entries


def test_2ca1(mongo_coll: Results) -> None:
    results = mongo_coll.find_one({"_id": "2ca1"})

    if results is None:
        pytest.fail(reason="No results")

    if results["interactions"] is None:
        pytest.fail(reason="No interactions")

    assert len(results["interactions"]) == 7
    assert results["errmsg"] is None


def test_2fyg(mongo_coll: Results) -> None:
    results = mongo_coll.find_one({"_id": "2fyg"})

    if results is None:
        pytest.fail(reason="No results")

    if results["interactions"] is None:
        pytest.fail(reason="No interactions")

    assert len(results["interactions"]) == 3
    assert results["errmsg"] is None


def test_1xak(mongo_coll: Results) -> None:
    results = mongo_coll.find_one({"_id": "1xak"})

    if results is None:
        pytest.fail(reason="No results")

    assert results["interactions"] is None
    assert results["errmsg"] == "No MET residues"


def test_2fxp(mongo_coll: Results) -> None:
    results = mongo_coll.find_one({"_id": "2fxp"})

    if results is None:
        pytest.fail(reason="No results")

    assert results["interactions"] is None
    assert results["errmsg"] == "No MET residues"


def test_6mwm(mongo_coll: Results) -> None:
    results = mongo_coll.find_one({"_id": "6mwm"})

    if results is None:
        pytest.fail(reason="No results")

    assert results["interactions"] is None
    assert results["errmsg"] == "No PHE/TYR/TRP residues"


def test_2cme(mongo_coll: Results) -> None:
    results = mongo_coll.find_one({"_id": "2cme"})

    if results is None:
        pytest.fail(reason="No results")

    assert results["interactions"] is None
    assert results["errmsg"] == "No Met-aromatic interactions"


def test_spam(mongo_coll: Results) -> None:
    results = mongo_coll.find_one({"_id": "spam"})

    if results is None:
        pytest.fail(reason="No results")

    assert results["interactions"] is None
    assert results["errmsg"] == "Invalid PDB entry 'spam'"


def test_check_valid_info_doc(mongo_coll_info: collection.Collection) -> None:
    results = mongo_coll_info.find_one({})

    if results is None:
        pytest.fail(reason="No results")

    assert results["chain"] == "A"
    assert results["cutoff_angle"] == 109.5
    assert results["cutoff_distance"] == 4.9
    assert results["model"] == "cp"
    assert results["num_workers"] == TestParams.num_threads
    assert results["number_of_entries"] == TestParams.num_entries
