#!/usr/bin/env python3
import sys
from os import path
from click import (
    group,
    argument,
    echo,
    secho,
    option,
    Path
)
from pytest import main as pytest_runner
from met_aromatic import MetAromatic
from parallel_processing import RunBatchQueries


@group()
def main():
    pass


@main.command()
@argument('code')
@option('--cutoff-distance', default=4.9, type=float, metavar='<distance-in-angstroms>')
@option('--cutoff-angle', default=109.5, type=float, metavar='<angle-in-degrees>')
@option('--chain', default='A', metavar='<chain>')
@option('--model', default='cp', metavar='<model>')
def single_met_aromatic_query(code, cutoff_distance, cutoff_angle, chain, model):
    header_success = ['ARO', 'POS', 'MET POS', 'NORM', 'MET-THETA', 'MET-PHI']
    results = MetAromatic(
        code,
        cutoff_distance=cutoff_distance,
        cutoff_angle=cutoff_angle,
        chain=chain,
        model=model
    ).get_met_aromatic_interactions()

    if results['exit_code'] == 0:
        echo("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*header_success))
        for line in results['results']:
            echo("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(*line.values()))
    else:
        secho(results['exit_status'], fg='red')
        secho(f"Exited with code: {results['exit_code']}", fg='red')
    sys.exit(results['exit_code'])


@main.command()
@argument('code')
@option('--cutoff-distance', default=4.9, type=float, metavar='<distance-in-angstroms>')
@option('--cutoff-angle', default=109.5, type=float, metavar='<angle-in-degrees>')
@option('--chain', default='A', metavar='<chain>')
@option('--model', default='cp', metavar='<model>')
@option('--vertices', default=3, type=int, metavar='<vertices>')
def single_bridging_interaction_query(code, cutoff_distance, cutoff_angle, chain, model, vertices):
    results = MetAromatic(
        code,
        cutoff_distance=cutoff_distance,
        cutoff_angle=cutoff_angle,
        chain=chain,
        model=model
    ).get_bridging_interactions(
        number_vertices=vertices
    )

    if results['exit_code'] == 0:
        echo(results['results'])
    else:
        secho(results['exit_status'], fg='red')
        secho(f"Exited with code: {results['exit_code']}", fg='red')
    sys.exit(results['exit_code'])


@main.command()
@argument('path_batch_file', type=Path('rb'))
@option('--cutoff-distance', default=4.9, type=float, metavar='<distance-in-angstroms>')
@option('--cutoff-angle', default=109.5, type=float, metavar='<angle-in-degrees>')
@option('--chain', default='A', metavar='<chain>')
@option('--model', default='cp', metavar='<model>')
@option('--threads', default=5, type=int, metavar='<number-threads>')
@option('--database', default='default_ma', metavar='<database-name>')
@option('--collection', default='default_ma', metavar='<collection-name>')
def run_batch_job(path_batch_file, cutoff_distance, cutoff_angle, chain, model, threads, database, collection):
    RunBatchQueries(
        path_batch_file, cutoff_distance, cutoff_angle,
        chain, model, threads, collection, database
    ).deploy_jobs()


@main.command()
@option('--verbose', '-v', is_flag=True)
@option('--exit-on-failure', '-x', is_flag=True)
@option('--test-expression', '-k', default=None)
def run_tests(verbose, exit_on_failure, test_expression):
    cmd = []
    cmd.append(path.dirname(path.abspath(__file__)))
    cmd.append('-s')
    if verbose:
        cmd.append('-v')
    if exit_on_failure:
        cmd.append('-x')
    if test_expression:
        cmd.append('-k' + test_expression)
    sys.exit(pytest_runner(cmd))


if __name__ == '__main__':
    main()
