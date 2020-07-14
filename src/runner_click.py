#!/usr/bin/env python3
import sys
from click import (
    group,
    argument,
    echo,
    secho,
    option,
    pass_context
)
from met_aromatic import MetAromatic


@group()
@option('--cutoff-distance', default=4.9, type=float, metavar='<distance-in-angstroms>')
@option('--cutoff-angle', default=109.5, type=float, metavar='<angle-in-degrees>')
@option('--chain', default='A', metavar='<chain>')
@option('--model', default='cp', metavar='<model>')
@pass_context
def main(context=None, cutoff_distance=None, cutoff_angle=None, chain=None, model=None):
    context.ensure_object(dict)
    context.obj['cutoff_distance'] = cutoff_distance
    context.obj['cutoff_angle'] = cutoff_angle
    context.obj['chain'] = chain
    context.obj['model'] = model


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
@option('--vertices', default=3, metavar='<vertices>')
def single_bridging_interaction_query(context, code, vertices):
    results = MetAromatic(
        code,
        cutoff_distance=context.obj['cutoff_distance'],
        cutoff_angle=context.obj['cutoff_angle'],
        chain=context.obj['chain'],
        model=context.obj['model']
    ).get_bridging_interactions(
        number_vertices=vertices
    )

    if results['exit_code'] == 0:
        echo(results['results'])
    else:
        secho(results['exit_status'], fg='red')
        secho(f"Exited with code: {results['exit_code']}", fg='red')
    sys.exit(results['exit_code'])


if __name__ == '__main__':
    main()
