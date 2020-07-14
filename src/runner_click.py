#!/usr/bin/env python3
import sys
from click import (
    group,
    argument,
    echo,
    secho,
    option
)
from met_aromatic import MetAromatic


@group()
def main():
    pass


@main.command()
@argument('code')
@option('--cutoff-distance', default=4.9, type=float)
@option('--cutoff-angle', default=109.5, type=float)
@option('--chain', default='A')
@option('--model', default='cp')
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
@option('--cutoff-distance', default=4.9, type=float)
@option('--cutoff-angle', default=109.5, type=float)
@option('--chain', default='A')
@option('--model', default='cp')
@option('--vertices', default=3, type=int)
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


if __name__ == '__main__':
    main()
