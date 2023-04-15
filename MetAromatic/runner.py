#!/usr/bin/env python3

# All Met-aromatic/pytest code is imported lazily within
# each click subcommand for significant performance improvements.
# Therefore disable C0415:

# pylint: disable=C0415   # Disable "Import outside toplevel" - we need this for lazy imports

import sys
import logging
import click
from core.helpers import consts

def setup_child_logger():

    logging.addLevelName(logging.ERROR, 'E')
    logging.addLevelName(logging.WARNING, 'W')
    logging.addLevelName(logging.INFO, 'I')
    logging.addLevelName(logging.DEBUG, 'D')

    logger = logging.getLogger('met-aromatic')
    logger.setLevel(logging.DEBUG)

    channel = logging.StreamHandler()
    formatter = logging.Formatter(fmt=consts.LOGRECORD_FORMAT, datefmt=consts.ISO_8601_DATE_FORMAT)
    channel.setFormatter(formatter)
    logger.addHandler(channel)

@click.group()
@click.option('--cutoff-distance', type=float, default=4.9, metavar='<Angstroms>')
@click.option('--cutoff-angle', type=float, default=109.5, metavar='<degrees>')
@click.option('--chain', default='A', metavar='<[A-Z]>')
@click.option('--model', type=click.Choice(['cp', 'rm']), default='cp', metavar='<cp|rm>')
@click.pass_context
def cli(context, **options):

    context.obj = options
    setup_child_logger()

@cli.command(help='Run a Met-aromatic query on a single PDB entry.')
@click.argument('code')
@click.pass_obj
def pair(obj, code):

    from core.pair import MetAromatic

    header_success = ['ARO', 'POS', 'MET POS', 'NORM', 'MET-THETA', 'MET-PHI']
    results = MetAromatic(**obj).get_met_aromatic_interactions(code)

    if not results.OK:
        sys.exit(results.STATUS)

    click.echo("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*header_success))

    for line in results.INTERACTIONS:
        click.echo("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*line.values()))

@cli.command(help='Run a bridging interaction query on a single PDB entry.')
@click.argument('code')
@click.option('--vertices', default=3, type=int, metavar='<vertices>')
@click.pass_obj
def bridge(obj, code, vertices):

    from core.bridge import GetBridgingInteractions

    results = GetBridgingInteractions(obj).get_bridging_interactions(vertices=vertices, code=code)

    if not results.OK:
        sys.exit(results.STATUS)

    click.echo(results.BRIDGES)

@cli.command(help='Run a Met-aromatic query batch job.')
@click.argument('path_batch_file', type=click.Path('rb'))
@click.option('--threads', default=5, type=int, metavar='<number-threads>', help='Specify number of workers to use.')
@click.option('--host', default='localhost', metavar='<hostname>', help='Specify host name.')
@click.option('--port', type=int, default=27017, metavar='<tcp-port>', help='Specify MongoDB TCP connection port.')
@click.option('-d', '--database', default='default_ma', metavar='<database-name>', help='Specify MongoDB database to use.')
@click.option('-c', '--collection', default='default_ma', metavar='<collection-name>', help='Specify MongoDB collection to use.')
@click.option('-x', '--overwrite', is_flag=True, default=False, help='Specify whether to overwrite collection specified with -c.')
@click.pass_obj
def batch(obj, **kwargs):

    from core.batch import ParallelProcessing
    ParallelProcessing({**kwargs, **obj}).main()

if __name__ == '__main__':
    cli()
