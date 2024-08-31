# pylint: disable=C0415   # Disable "Import outside toplevel" - we need this for lazy imports

from pathlib import Path
import sys
import click
from .aliases import Models
from .consts import Help
from .errors import SearchError
from .models import MetAromaticParams, BatchParams


@click.group()
@click.option(
    "--cutoff-distance", default=4.9, help=Help.DIST.value, type=click.FloatRange(min=0)
)
@click.option(
    "--cutoff-angle",
    default=109.5,
    help=Help.ANGLE.value,
    type=click.FloatRange(min=0, max=360),
)
@click.option("--chain", default="A", help=Help.CHAIN.value)
@click.option(
    "--model", default="cp", help=Help.MODEL.value, type=click.Choice(["cp", "rm"])
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


@cli.command(help=Help.CMD_PAIR.value)
@click.argument("pdb_code")
@click.pass_obj
def pair(obj: MetAromaticParams, pdb_code: str) -> None:
    from .get_pair import get_pairs_from_pdb, print_interactions

    try:
        print_interactions(
            get_pairs_from_pdb(
                chain=obj.chain,
                cutoff_angle=obj.cutoff_angle,
                cutoff_distance=obj.cutoff_distance,
                model=obj.model,
                pdb_code=pdb_code,
            )
        )
    except SearchError as error:
        sys.exit(str(error))


@cli.command(help=Help.CMD_READ_LOCAL.value)
@click.argument(
    "pdb_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.pass_obj
def read_local(obj: MetAromaticParams, pdb_file: Path) -> None:
    from .get_pair import get_pairs_from_file, print_interactions

    try:
        print_interactions(
            get_pairs_from_file(
                chain=obj.chain,
                cutoff_angle=obj.cutoff_angle,
                cutoff_distance=obj.cutoff_distance,
                filepath=pdb_file,
                model=obj.model,
            )
        )
    except SearchError as error:
        sys.exit(str(error))


@cli.command(help=Help.CMD_BRIDGE.value)
@click.argument("code")
@click.option(
    "--vertices", default=3, type=click.IntRange(min=3), help=Help.VERTICES.value
)
@click.pass_obj
def bridge(obj: MetAromaticParams, code: str, vertices: int) -> None:
    from .get_bridge import get_bridges, print_bridges

    try:
        print_bridges(
            get_bridges(
                chain=obj.chain,
                code=code,
                cutoff_angle=obj.cutoff_angle,
                cutoff_distance=obj.cutoff_distance,
                model=obj.model,
                vertices=vertices,
            )
        )
    except SearchError as error:
        sys.exit(str(error))


@cli.command(help=Help.CMD_BATCH.value)
@click.argument(
    "batch_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--threads", default=5, type=click.IntRange(min=1, max=15), help=Help.THREADS.value
)
@click.option("--host", default="localhost", help=Help.HOST.value)
@click.option("--port", type=int, default=27017, help=Help.PORT.value)
@click.option("-d", "--database", default="default_ma", help=Help.DB.value)
@click.option("-c", "--collection", default="default_ma", help=Help.COLL.value)
@click.option(
    "-x", "--overwrite", is_flag=True, default=False, help=Help.OVERWRITE.value
)
@click.option("-u", "--username", prompt=True, help=Help.USERNAME.value)
@click.option(
    "-p", "--password", prompt=True, hide_input=True, help=Help.PASSWORD.value
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
