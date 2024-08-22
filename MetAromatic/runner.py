# pylint: disable=C0415   # Disable "Import outside toplevel" - we need this for lazy imports
# pylint: disable=C0301   # Disable "Line too long"

from typing import Literal
import sys
import logging
import click
from .consts import LOGRECORD_FORMAT, ISO_8601_DATE_FORMAT
from .errors import SearchError
from .models import MetAromaticParams, BatchParams, FeatureSpace, BridgeSpace


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
    default=4.9,
    help="Specify a cutoff distance in Angstroms",
    type=click.FloatRange(min=0),
)
@click.option(
    "--cutoff-angle",
    default=109.5,
    help="Specify a cutoff angle in degrees",
    type=click.FloatRange(min=0, max=360),
)
@click.option("--chain", default="A", help="Specify a chain ID")
@click.option(
    "--model",
    default="cp",
    help="Specify a lone pair interpolation model",
    type=click.Choice(["cp", "rm"]),
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


def get_pairs_from_local_file(source: str, params: MetAromaticParams) -> FeatureSpace:
    from .pair import MetAromaticLocal

    return MetAromaticLocal(params).get_met_aromatic_interactions(source)


def get_pairs_from_pdb(source: str, params: MetAromaticParams) -> FeatureSpace:
    from .pair import MetAromatic

    return MetAromatic(params).get_met_aromatic_interactions(source)


@cli.command(help="Run a Met-aromatic query on a single PDB entry.")
@click.option(
    "--read-local",
    is_flag=True,
    default=False,
    help="Specify whether to read a local PDB file.",
)
@click.argument("source")
@click.pass_obj
def pair(obj: MetAromaticParams, read_local: bool, source: str) -> None:
    try:
        fs: FeatureSpace
        if read_local:
            fs = get_pairs_from_local_file(source, obj)
        else:
            fs = get_pairs_from_pdb(source, obj)

        fs.print_interactions()
    except SearchError:
        sys.exit("Search failed!")


@cli.command(help="Run a bridging interaction query on a single PDB entry.")
@click.argument("code")
@click.option(
    "--vertices",
    default=3,
    type=click.IntRange(min=3),
    help="Specify number of vertices",
)
@click.pass_obj
def bridge(obj: MetAromaticParams, code: str, vertices: int) -> None:
    from .bridge import get_bridges

    try:
        bs: BridgeSpace = get_bridges(params=obj, code=code, vertices=vertices)
        bs.print_bridges()
    except SearchError:
        sys.exit("Search failed!")


@cli.command(help="Run a Met-aromatic query batch job.")
@click.argument("path_batch_file")
@click.option(
    "--threads",
    default=5,
    type=click.IntRange(min=1, max=15),
    help="Specify number of workers to use.",
)
@click.option("--host", default="localhost", help="Specify host name.")
@click.option(
    "--port", type=int, default=27017, help="Specify MongoDB TCP connection port."
)
@click.option(
    "-d", "--database", default="default_ma", help="Specify MongoDB database to use."
)
@click.option(
    "-c",
    "--collection",
    default="default_ma",
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
    "--username",
    prompt=True,
    help="Specify MongoDB username if authentication is enabled.",
)
@click.option(
    "-p",
    "--password",
    prompt=True,
    hide_input=True,
    help="Specify MongoDB password if authentication is enabled.",
)
@click.pass_obj
def batch(
    obj: MetAromaticParams,
    collection: str,
    database: str,
    host: str,
    overwrite: bool,
    password: str,
    path_batch_file: str,
    port: int,
    threads: int,
    username: str,
) -> None:
    from MetAromatic.batch import ParallelProcessing

    params = BatchParams(
        collection=collection,
        database=database,
        host=host,
        overwrite=overwrite,
        password=password,
        path_batch_file=path_batch_file,
        port=port,
        threads=threads,
        username=username,
    )

    try:
        ParallelProcessing(obj, params).main()
    except SearchError:
        sys.exit("Search failed!")


if __name__ == "__main__":
    cli()
