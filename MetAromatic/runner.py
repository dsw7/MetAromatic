#!/usr/bin/env python3

# All Met-aromatic/pytest code is imported lazily within
# each click subcommand for significant performance improvements.
# Therefore disable C0415:

# pylint: disable=C0415   # Disable "Import outside toplevel" - we need this for lazy imports

import sys
import logging
from configparser import ConfigParser
from pathlib import Path
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
@click.option('--cutoff-distance', type=float, default=None, help='Override cutoff distance defined in *.ini file.', metavar='<Angstroms>')
@click.option('--cutoff-angle', type=float, default=None, help='Override cutoff angle defined in *.ini file.', metavar='<degrees>')
@click.option('--chain', default=None, help='Override chain defined in *.ini file.', metavar='<[A-Z]>')
@click.option('--model', default=None, help='Override lone pair interpolation model defined in *.ini file.', metavar='<cp|rm>')
@click.pass_context
def cli(context, **options):

    path_ini = Path(__file__).resolve().parent / 'runner.ini'

    if not path_ini.exists():
        sys.exit(f'Could not find initialization file: {path_ini}')

    parser = ConfigParser()
    parser.read(path_ini)

    context.obj = {
        'cutoff_distance': parser['root-configs'].getfloat('cutoff-distance'),
        'cutoff_angle': parser['root-configs'].getfloat('cutoff-angle'),
        'chain': parser['root-configs']['chain'],
        'model': parser['root-configs']['model']
    }

    if options['cutoff_distance']:
        context.obj['cutoff_distance'] = options['cutoff_distance']

    if options['cutoff_angle']:
        context.obj['cutoff_angle'] = options['cutoff_angle']

    if options['chain']:
        context.obj['chain'] = options['chain']

    if options['model']:
        context.obj['model'] = options['model']

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

    obj_bridge = GetBridgingInteractions(obj)
    if obj_bridge.get_bridging_interactions(vertices=vertices, code=code):
        obj_bridge.display_results()

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
