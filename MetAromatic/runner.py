#!/usr/bin/env python3

# All Met-aromatic/pytest code is imported lazily within
# each click subcommand for significant performance improvements.
# Therefore disable C0415:

# pylint: disable=C0415   # Disable "Import outside toplevel" - we need this for lazy imports
# pylint: disable=C0301   # Disable "Line too long"

from os import get_terminal_size
from typing import Union, Dict
import sys
import logging
import click
from core.helpers import consts

try:
    SEPARATOR = get_terminal_size()[0] * '-'
except OSError:
    SEPARATOR = 25 * '-'

def setup_child_logger(debug: bool) -> None:

    logging.addLevelName(logging.ERROR, 'E')
    logging.addLevelName(logging.WARNING, 'W')
    logging.addLevelName(logging.INFO, 'I')
    logging.addLevelName(logging.DEBUG, 'D')

    logger = logging.getLogger('met-aromatic')

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    channel = logging.StreamHandler()
    formatter = logging.Formatter(fmt=consts.LOGRECORD_FORMAT, datefmt=consts.ISO_8601_DATE_FORMAT)
    channel.setFormatter(formatter)
    logger.addHandler(channel)

@click.group()
@click.option('--debug', is_flag=True, default=False, help='Enable debug logging')
@click.option('--cutoff-distance', type=click.FloatRange(min=0), default=4.9, metavar='<Angstroms>')
@click.option('--cutoff-angle', type=click.FloatRange(min=0, max=360), default=109.5, metavar='<degrees>')
@click.option('--chain', default='A', metavar='<[A-Z]>')
@click.option('--model', type=click.Choice(['cp', 'rm']), default='cp', metavar='<cp|rm>')
@click.pass_context
def cli(context: click.core.Context, debug: bool, **options: Union[str, float]) -> None:

    context.obj = options
    setup_child_logger(debug=debug)

@cli.command(help='Run a Met-aromatic query on a single PDB entry.')
@click.argument('code')
@click.pass_obj
def pair(obj: Dict[str, Union[str, float]], code: str) -> None:

    from core.pair import MetAromatic

    results = MetAromatic(**obj).get_met_aromatic_interactions(code)

    if not results.OK:
        sys.exit(results.STATUS)

    click.echo(SEPARATOR)

    header_success = ['ARO', 'POS', 'MET POS', 'NORM', 'MET-THETA', 'MET-PHI']
    click.echo("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*header_success))

    click.echo(SEPARATOR)

    for line in results.INTERACTIONS:
        click.echo("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*line.values()))

    click.echo(SEPARATOR)

@cli.command(help='Run a bridging interaction query on a single PDB entry.')
@click.argument('code')
@click.option('--vertices', default=3, type=click.IntRange(min=3), metavar='<vertices>')
@click.pass_obj
def bridge(obj: Dict[str, Union[str, float]], code: str, vertices: int) -> None:

    from core.bridge import GetBridgingInteractions

    results = GetBridgingInteractions(obj).get_bridging_interactions(vertices=vertices, code=code)

    if not results.OK:
        sys.exit(results.STATUS)

    click.echo(SEPARATOR)

    for line in results.BRIDGES:
        click.echo('{' + '}-{'.join(line) + '}')

    click.echo(SEPARATOR)

@cli.command(help='Run a Met-aromatic query batch job.')
@click.argument('path_batch_file', type=click.Path('rb'))
@click.option('--threads', default=5, type=int, metavar='<number-threads>', help='Specify number of workers to use.')
@click.option('--host', default='localhost', metavar='<hostname>', help='Specify host name.')
@click.option('--port', type=int, default=27017, metavar='<tcp-port>', help='Specify MongoDB TCP connection port.')
@click.option('-d', '--database', default='default_ma', metavar='<database-name>', help='Specify MongoDB database to use.')
@click.option('-c', '--collection', default='default_ma', metavar='<collection-name>', help='Specify MongoDB collection to use.')
@click.option('-x', '--overwrite', is_flag=True, default=False, help='Specify whether to overwrite collection specified with -c.')
@click.pass_obj
def batch(obj: Dict[str, Union[str, float]], **options: Union[str, float]) -> None:

    from core.batch import ParallelProcessing
    ParallelProcessing({**options, **obj}).main()

if __name__ == '__main__':
    cli()
