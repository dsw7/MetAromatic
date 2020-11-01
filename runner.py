#!/usr/bin/env python3
import sys
from os import path
from tempfile import gettempdir
from click import (
    group,
    argument,
    echo,
    secho,
    option,
    Path
)

# all Met-aromatic/pytest code is imported lazily within
# each click subcommand for significant performance improvements

@group()
def main():
    pass

@main.command(help='Run single Met-aromatic query in a curses interface.')
@argument('code')
@option('--cutoff-distance', default='4.9', metavar='<distance-in-angstroms>')
@option('--cutoff-angle', default='109.5', metavar='<angle-in-degrees>')
@option('--chain', default='A', metavar='<chain>')
@option('--model', default='cp', metavar='<model>')
def interface(code, cutoff_distance, cutoff_angle, chain, model):
    from utils.frontend import MetAromaticTUI
    parameters = {
        'code': code,
        'cutoff_distance': cutoff_distance,
        'cutoff_angle': cutoff_angle,
        'chain': chain,
        'model': model
    }
    sys.exit(MetAromaticTUI(parameters).event_loop())

@main.command(help='Run a Met-aromatic query on a single PDB entry.')
@argument('code')
@option('--cutoff-distance', default=4.9, type=float, metavar='<distance-in-angstroms>')
@option('--cutoff-angle', default=109.5, type=float, metavar='<angle-in-degrees>')
@option('--chain', default='A', metavar='<chain>')
@option('--model', default='cp', metavar='<model>')
def single_met_aromatic_query(code, cutoff_distance, cutoff_angle, chain, model):
    from utils.met_aromatic import MetAromatic
    header_success = ['ARO', 'POS', 'MET POS', 'NORM', 'MET-THETA', 'MET-PHI']
    results = MetAromatic(
        cutoff_distance=cutoff_distance, cutoff_angle=cutoff_angle, chain=chain, model=model
    ).get_met_aromatic_interactions(code)

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
@option('--cutoff-distance', default=4.9, type=float, metavar='<distance-in-angstroms>')
@option('--cutoff-angle', default=109.5, type=float, metavar='<angle-in-degrees>')
@option('--chain', default='A', metavar='<chain>')
@option('--model', default='cp', metavar='<model>')
@option('--vertices', default=3, type=int, metavar='<vertices>')
def single_bridging_interaction_query(code, cutoff_distance, cutoff_angle, chain, model, vertices):
    from utils.met_aromatic import MetAromatic
    results = MetAromatic(
        cutoff_distance=cutoff_distance, cutoff_angle=cutoff_angle, chain=chain, model=model
    ).get_bridging_interactions(
        number_vertices=vertices, code=code
    )

    if results['exit_code'] == 0:
        echo(results['results'])
    else:
        secho(results['exit_status'], fg='red')
        secho(f"Exited with code: {results['exit_code']}", fg='red')
    sys.exit(results['exit_code'])

@main.command(help='Run a Met-aromatic query batch job.')
@argument('path_batch_file', type=Path('rb'))
@option('--cutoff-distance', default=4.9, type=float, metavar='<distance-in-angstroms>')
@option('--cutoff-angle', default=109.5, type=float, metavar='<angle-in-degrees>')
@option('--chain', default='A', metavar='<chain>')
@option('--model', default='cp', metavar='<model>')
@option('--threads', default=5, type=int, metavar='<number-threads>')
@option('--database', default='default_ma', metavar='<database-name>')
@option('--collection', default='default_ma', metavar='<collection-name>')
@option('--stream/--no-stream', default=False, help='Log to stdout instead of file')
def run_batch_job(path_batch_file, cutoff_distance, cutoff_angle, chain, model, threads, database, collection, stream):
    from utils.parallel_processing import RunBatchQueries
    parameters = {
        'path_batch_file': path_batch_file,
        'cutoff_distance': cutoff_distance,
        'cutoff_angle': cutoff_angle,
        'chain': chain,
        'model': model,
        'threads': threads,
        'database': database,
        'collection': collection,
        'stream': stream
    }
    sys.exit(RunBatchQueries(parameters).deploy_jobs())

@main.command(help='Run internal unit tests.')
@option('--verbose', '-v', is_flag=True)
@option('--exit-on-failure', '-x', is_flag=True)
@option('--test-expression', '-k', default=None)
def run_tests(verbose, exit_on_failure, test_expression):
    from pytest import main as test_main
    command = []
    command.append(path.dirname(path.abspath(__file__)))
    command.append('-s')
    if verbose:
        command.append('-v')
    if exit_on_failure:
        command.append('-x')
    if test_expression:
        command.append('-k' + test_expression)
    sys.exit(test_main(command))

@main.command(help='Run internal unit tests with coverage.')
@option('--verbose', '-v', is_flag=True)
@option('--exit-on-failure', '-x', is_flag=True)
@option('--test-expression', '-k', default=None)
@option('--path-to-html', default=path.join(gettempdir(), 'htmlcov'), metavar='/path/to/htmlcov/')
def run_tests_with_coverage(verbose, exit_on_failure, test_expression, path_to_html):
    from pytest import main as test_main
    root = path.dirname(path.abspath(__file__))
    command = []
    command.append(root)
    command.append('-s')
    if verbose:
        command.append('-v')
    if exit_on_failure:
        command.append('-x')
    if test_expression:
        command.append('-k' + test_expression)
    command.append(f'--cov={root}')
    command.append(f'--cov-report=html:{path_to_html}')
    command.append(f'--cov-config={path.join(root, ".coveragerc")}')
    sys.exit(test_main(command))

if __name__ == '__main__':
    main()
