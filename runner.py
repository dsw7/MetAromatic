#!/usr/bin/env python3

# All Met-aromatic/pytest code is imported lazily within
# each click subcommand for significant performance improvements.
# Therefore disable C0415:

# pylint: disable=C0415   # Disable "Import outside toplevel" - we need this for lazy imports

import sys
from configparser import ConfigParser
from os import path
from click import (
    group,
    argument,
    echo,
    secho,
    option,
    Path,
    pass_context,
    pass_obj
)
from src.primitives.consts import EXIT_FAILURE

@group()
@pass_context
def main(context):
    path_ini = path.join(path.dirname(__file__), 'met_aromatic.ini')

    if not path.exists(path_ini):
        secho('Could not find initialization file: {}'.format(path_ini), fg='red')
        sys.exit(EXIT_FAILURE)

    parser = ConfigParser()
    parser.read(path_ini)

    context.obj = {
        'cutoff_distance': parser['root-configs'].getfloat('cutoff-distance'),
        'cutoff_angle': parser['root-configs'].getfloat('cutoff-angle'),
        'chain': parser['root-configs']['chain'],
        'model': parser['root-configs']['model']
    }

@main.command(help='Run single Met-aromatic query in a curses interface.')
@argument('code')
@pass_obj
def interface(obj, code):
    from src.frontend import MetAromaticTUI
    obj['code'] = code
    sys.exit(MetAromaticTUI(obj).event_loop())

@main.command(help='Run a Met-aromatic query on a single PDB entry.')
@argument('code')
@option('--cutoff-distance', type=float, default=None, help='Override cutoff distance defined in *.ini file.', metavar='<Angstroms>')
@option('--cutoff-angle', type=float, default=None, help='Override cutoff angle defined in *.ini file.', metavar='<degrees>')
@option('--chain', default=None, help='Override chain defined in *.ini file.', metavar='<[A-Z]>')
@option('--model', default=None, help='Override lone pair interpolation model defined in *.ini file.', metavar='<cp|rm>')
@pass_obj
def pair(obj, code, cutoff_distance, cutoff_angle, chain, model):

    if cutoff_distance:
        obj['cutoff_distance'] = cutoff_distance

    if cutoff_angle:
        obj['cutoff_angle'] = cutoff_angle

    if chain:
        obj['chain'] = chain

    if model:
        obj['model'] = model

    from src.met_aromatic import MetAromatic

    header_success = ['ARO', 'POS', 'MET POS', 'NORM', 'MET-THETA', 'MET-PHI']
    results = MetAromatic(**obj).get_met_aromatic_interactions(code)

    if results['exit_code'] == 0:
        echo("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*header_success))
        for line in results['results']:
            echo("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*line.values()))
    else:
        secho(results['exit_status'], fg='red')
        secho(f"Exited with code: {results['exit_code']}", fg='red')

    sys.exit(results['exit_code'])

@main.command(help='Run a bridging interaction query on a single PDB entry.')
@argument('code')
@option('--vertices', default=3, type=int, metavar='<vertices>')
@pass_obj
def bridge(obj, code, vertices):
    if vertices < 3:
        secho('Vertices must be > 2', fg='red')
        sys.exit(EXIT_FAILURE)

    from src.met_aromatic import GetBridgingInteractions
    results = GetBridgingInteractions(**obj).get_bridging_interactions(
        vertices=vertices, code=code
    )

    if results['exit_code'] == 0:
        echo(results['results'])
    else:
        secho(results['exit_status'], fg='red')
        secho(f"Exited with code: {results['exit_code']}", fg='red')

    sys.exit(results['exit_code'])

@main.command(help='Run a Met-aromatic query batch job.')
@argument('path_batch_file', type=Path('rb'))
@option('--threads', default=5, type=int, metavar='<number-threads>')
@option('--database', default='default_ma', metavar='<database-name>')
@option('--collection', default='default_ma', metavar='<collection-name>')
@pass_obj
def batch(obj, path_batch_file, threads, database, collection):
    from src.parallel_processing import RunBatchQueries
    options = {
        'path_batch_file': path_batch_file,
        'threads': threads,
        'database': database,
        'collection': collection
    }

    all_options = {
        **options,
        **obj
    }
    RunBatchQueries(all_options).deploy_jobs()

if __name__ == '__main__':
    main()
