# pylint: disable=C0415   # Disable "Import outside toplevel" - we need this for lazy imports
# pylint: disable=C0301   # Disable "Line too long"

from typing import Literal
import sys
import logging
import click
from typing_extensions import Unpack
from MetAromatic.consts import LOGRECORD_FORMAT, ISO_8601_DATE_FORMAT
from MetAromatic.complex_types import TYPE_BATCH_PARAMS
from .models import MetAromaticParams
from .utils import print_separator


def setup_child_logger(debug: bool) -> None:
    logging.addLevelName(logging.ERROR, "E")
    logging.addLevelName(logging.WARNING, "W")
    logging.addLevelName(logging.INFO, "I")
    logging.addLevelName(logging.DEBUG, "D")

    logger = logging.getLogger("met-aromatic")

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    channel = logging.StreamHandler()
    formatter = logging.Formatter(fmt=LOGRECORD_FORMAT, datefmt=ISO_8601_DATE_FORMAT)
    channel.setFormatter(formatter)
    logger.addHandler(channel)


@click.group()
@click.option("--debug", is_flag=True, default=False, help="Enable debug logging")
@click.option(
    "--cutoff-distance",
    type=click.FloatRange(min=0),
    default=4.9,
    metavar="<Angstroms>",
)
@click.option(
    "--cutoff-angle",
    type=click.FloatRange(min=0, max=360),
    default=109.5,
    metavar="<degrees>",
)
@click.option("--chain", default="A", metavar="<[A-Z]>")
@click.option(
    "--model", type=click.Choice(["cp", "rm"]), default="cp", metavar="<cp|rm>"
)
@click.pass_context
def cli(
    context: click.core.Context,
    debug: bool,
    chain: str,
    cutoff_angle: float,
    cutoff_distance: float,
    model: Literal["cp", "rm"],
) -> None:
    context.obj = MetAromaticParams(
        chain=chain,
        cutoff_angle=cutoff_angle,
        cutoff_distance=cutoff_distance,
        model=model,
    )
    setup_child_logger(debug=debug)


@cli.command(help="Run a Met-aromatic query on a single PDB entry.")
@click.option(
    "--read-local",
    is_flag=True,
    default=False,
    help="Specify whether to read a local PDB file",
)
@click.argument("source")
@click.pass_obj
def pair(obj: MetAromaticParams, read_local: bool, source: str) -> None:
    if read_local:
        from MetAromatic.pair import MetAromaticLocal

        results = MetAromaticLocal(obj).get_met_aromatic_interactions(source)
    else:
        from MetAromatic.pair import MetAromatic

        results = MetAromatic(obj).get_met_aromatic_interactions(source)

    if not results["OK"]:
        sys.exit(results["status"])

    print_separator()

    header_success = ["ARO", "POS", "MET POS", "NORM", "MET-THETA", "MET-PHI"]
    click.echo("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*header_success))

    print_separator()

    for line in results["interactions"]:
        click.echo("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*line.values()))

    print_separator()


@cli.command(help="Run a bridging interaction query on a single PDB entry.")
@click.argument("code")
@click.option("--vertices", default=3, type=click.IntRange(min=3), metavar="<vertices>")
@click.pass_obj
def bridge(obj: MetAromaticParams, code: str, vertices: int) -> None:
    from MetAromatic.bridge import GetBridgingInteractions

    results = GetBridgingInteractions(obj).get_bridging_interactions(
        vertices=vertices, code=code
    )

    if not results["OK"]:
        sys.exit(results["status"])

    print_separator()

    for line in results["bridges"]:
        click.echo("{" + "}-{".join(line) + "}")

    print_separator()


@cli.command(help="Run a Met-aromatic query batch job.")
@click.argument("path_batch_file")
@click.option(
    "--threads",
    default=5,
    type=int,
    metavar="<number-threads>",
    help="Specify number of workers to use.",
)
@click.option(
    "--host", default="localhost", metavar="<hostname>", help="Specify host name."
)
@click.option(
    "--port",
    type=int,
    default=27017,
    metavar="<tcp-port>",
    help="Specify MongoDB TCP connection port.",
)
@click.option(
    "-d",
    "--database",
    default="default_ma",
    metavar="<database-name>",
    help="Specify MongoDB database to use.",
)
@click.option(
    "-c",
    "--collection",
    default="default_ma",
    metavar="<collection-name>",
    help="Specify MongoDB collection to use.",
)
@click.option(
    "-x",
    "--overwrite",
    is_flag=True,
    default=False,
    help="Specify whether to overwrite collection specified with -c.",
)
@click.option(
    "-u",
    "--uri",
    metavar="<mongodb://{username}:{password}@{host}:{port}/>",
    help="Specify MongoDB connection URI.",
)
@click.pass_obj
def batch(obj: MetAromaticParams, **batch_params: Unpack[TYPE_BATCH_PARAMS]) -> None:
    from MetAromatic.batch import ParallelProcessing

    ParallelProcessing(obj, batch_params).main()


if __name__ == "__main__":
    cli()
