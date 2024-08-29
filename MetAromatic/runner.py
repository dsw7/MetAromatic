# pylint: disable=C0415   # Disable "Import outside toplevel" - we need this for lazy imports
# pylint: disable=C0301   # Disable "Line too long"

from pathlib import Path
import sys
import click
from .aliases import Models
from .errors import SearchError
from .models import MetAromaticParams, BatchParams


@click.group()
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
    chain: str,
    cutoff_angle: float,
    cutoff_distance: float,
    model: Models,
) -> None:
    context.obj = MetAromaticParams(
        chain=chain,
        cutoff_angle=cutoff_angle,
        cutoff_distance=cutoff_distance,
        model=model,
    )


@cli.command(help="Run a Met-aromatic query against a single PDB entry.")
@click.argument("pdb_code")
@click.pass_obj
def pair(obj: MetAromaticParams, pdb_code: str) -> None:
    from .get_pair import get_pairs_from_pdb, print_interactions

    try:
        print_interactions(
            get_pairs_from_pdb(
                pdb_code=pdb_code,
                chain=obj.chain,
                cutoff_angle=obj.cutoff_angle,
                cutoff_distance=obj.cutoff_distance,
                model=obj.model,
            )
        )
    except SearchError as error:
        sys.exit(str(error))


@cli.command(help="Run a Met-aromatic query against a local PDB file.")
@click.argument(
    "pdb_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.pass_obj
def read_local(obj: MetAromaticParams, pdb_file: Path) -> None:
    from .get_pair import get_pairs_from_file, print_interactions

    try:
        print_interactions(get_pairs_from_file(filepath=pdb_file, params=obj))
    except SearchError as error:
        sys.exit(str(error))


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
    from .get_bridge import get_bridges, print_bridges

    try:
        print_bridges(get_bridges(params=obj, code=code, vertices=vertices))
    except SearchError as error:
        sys.exit(str(error))


@cli.command(help="Run a Met-aromatic query batch job.")
@click.argument(
    "batch_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
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
    batch_file: Path,
    collection: str,
    database: str,
    host: str,
    overwrite: bool,
    password: str,
    port: int,
    threads: int,
    username: str,
) -> None:
    from .get_batch import run_batch_job

    bp = BatchParams(
        collection=collection,
        database=database,
        host=host,
        overwrite=overwrite,
        password=password,
        path_batch_file=batch_file,
        port=port,
        threads=threads,
        username=username,
    )
    try:
        run_batch_job(params=obj, bp=bp)
    except SearchError as error:
        sys.exit(str(error))


if __name__ == "__main__":
    cli()
