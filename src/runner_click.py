#!/usr/bin/env python3
import sys
from tempfile import gettempdir
from os import path
from click import (
    group,
    argument,
    echo,
    secho,
    option,
    pass_context,
    Path
)
from met_aromatic import MetAromatic
from parallel_processing import RunBatchQueries


@group()
@option('--cutoff-distance', default=4.9, type=float, metavar='<distance-in-angstroms>')
@option('--cutoff-angle', default=109.5, type=float, metavar='<angle-in-degrees>')
@option('--chain', default='A', metavar='<chain>')
@option('--model', default='cp', metavar='<model>')
@option('--vertices', default=3, type=int, metavar='<vertices>')
@option('--threads', default=5, type=int, metavar='<number-threads>')
@option('--database', default='default_ma', metavar='<database-name>')
@option('--collection', default='default_ma', metavar='<collection-name>')
@option('--host', default='localhost', metavar='<hostname>')
@option('--port', default=27017, type=int, metavar='<port>')
@option('--path-log-file', default=path.join(gettempdir(), 'met_aromatic.log'), type=Path('wb'), metavar='<path/file.log>')
@pass_context
def main(context=None, cutoff_distance=None, cutoff_angle=None, chain=None, model=None, vertices=None,
         threads=None, database=None, collection=None, host=None, port=None, path_log_file=None):

    context.ensure_object(dict)
    context.obj['cutoff_distance'] = cutoff_distance
    context.obj['cutoff_angle'] = cutoff_angle
    context.obj['chain'] = chain
    context.obj['model'] = model
    context.obj['vertices'] = vertices
    context.obj['threads'] = threads
    context.obj['database'] = database
    context.obj['collection'] = collection
    context.obj['host'] = host
    context.obj['port'] = port
    context.obj['path_logfile'] = path_log_file


@main.command()
@pass_context
@argument('code')
def single_met_aromatic_query(context, code):
    header_success = ['ARO', 'POS', 'MET POS', 'NORM', 'MET-THETA', 'MET-PHI']
    results = MetAromatic(
        code,
        cutoff_distance=context.obj['cutoff_distance'],
        cutoff_angle=context.obj['cutoff_angle'],
        chain=context.obj['chain'],
        model=context.obj['model']
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
@pass_context
@argument('code')
def single_bridging_interaction_query(context, code):
    results = MetAromatic(
        code,
        cutoff_distance=context.obj['cutoff_distance'],
        cutoff_angle=context.obj['cutoff_angle'],
        chain=context.obj['chain'],
        model=context.obj['model']
    ).get_bridging_interactions(
        number_vertices=context.obj['vertices']
    )

    if results['exit_code'] == 0:
        echo(results['results'])
    else:
        secho(results['exit_status'], fg='red')
        secho(f"Exited with code: {results['exit_code']}", fg='red')
    sys.exit(results['exit_code'])


@main.command()
@pass_context
@argument('path_batch_file', type=Path('rb'))
def run_batch_job(context, path_batch_file):
    RunBatchQueries(path_batch_file, context).deploy_jobs()


if __name__ == '__main__':
    main()
