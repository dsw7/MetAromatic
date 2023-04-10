#!/usr/bin/env python3

# All Met-aromatic/pytest code is imported lazily within
# each click subcommand for significant performance improvements.
# Therefore disable C0415:

# pylint: disable=C0415   # Disable "Import outside toplevel" - we need this for lazy imports

import sys
from configparser import ConfigParser
from pathlib import Path
import click
from core.helpers import consts

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

@cli.command(help='Run a Met-aromatic query on a single PDB entry.')
@click.argument('code')
@click.pass_obj
def pair(obj, code):

    from core.pair import MetAromatic

    header_success = ['ARO', 'POS', 'MET POS', 'NORM', 'MET-THETA', 'MET-PHI']
    results = MetAromatic(**obj).get_met_aromatic_interactions(code)

    if results['exit_code'] == 0:
        click.echo("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*header_success))
        for line in results['results']:
            click.echo("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*line.values()))

    else:
        click.secho(results['exit_status'], fg='red')
        click.secho('Exited with code: {}'.format(results['exit_code']), fg='red')

    sys.exit(results['exit_code'])

@cli.command(help='Run a bridging interaction query on a single PDB entry.')
@click.argument('code')
@click.option('--vertices', default=3, type=int, metavar='<vertices>')
@click.pass_obj
def bridge(obj, code, vertices):

    if vertices < consts.MINIMUM_VERTICES:
        sys.exit(f'Vertices must be >= {consts.MINIMUM_VERTICES}')

    from core.bridge import GetBridgingInteractions

    results = GetBridgingInteractions(**obj).get_bridging_interactions(
        vertices=vertices, code=code
    )

    if results['exit_code'] == 0:
        click.echo(results['results'])
    else:
        click.secho(results['exit_status'], fg='red')
        click.secho('Exited with code: {}'.format(results['exit_code']), fg='red')

    sys.exit(results['exit_code'])

@cli.command(help='Run a Met-aromatic query batch job.')
@click.argument('path_batch_file', type=click.Path('rb'))
@click.option('--threads', default=5, type=int, metavar='<number-threads>', help='Specify number of workers to use.')
@click.option('--timeout', default=1.00, type=float, metavar='<timeout-in-seconds>', help='Specify MongoDB connection timeout in seconds.')
@click.option('--host', default='localhost', metavar='<hostname>', help='Specify host name.')
@click.option('--port', type=int, default=27017, metavar='<tcp-port>', help='Specify MongoDB TCP connection port.')
@click.option('-u', '--username', default=None, metavar='<username>', help='Specify MongoDB username if authentication enabled.')
@click.option('-p', '--password', default=None, metavar='<password>', help='Specify MongoDB password if authentication enabled.')
@click.option('-d', '--database', default='default_ma', metavar='<database-name>', help='Specify MongoDB database to use.')
@click.option('-c', '--collection', default='default_ma', metavar='<collection-name>', help='Specify MongoDB collection to use.')
@click.option('-x', '--overwrite', is_flag=True, default=False, help='Specify whether to overwrite collection specified with -c.')
@click.pass_obj
def batch(obj, **kwargs):

    from core.batch import ParallelProcessing
    ParallelProcessing({**kwargs, **obj}).deploy_jobs()

if __name__ == '__main__':
    cli()
