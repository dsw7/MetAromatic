from re import match
from .regex_patterns import (
    pattern_regex_met,
    pattern_regex_phe,
    pattern_regex_tyr,
    pattern_regex_trp
)

def get_raw_data_from_file(filepath):
    try:
        with open(filepath, 'r') as file:
            raw_data = [line for line in file]
    except FileNotFoundError:
        return False
    else:
        return raw_data

def get_first_model_from_raw_data(raw_data):
    first_model = []
    for line in raw_data:
        if 'ENDMDL' not in line:
            first_model.append(line)
        else:
            break
    return first_model

def get_relevant_met_coordinates(first_model, chain):
    return [line.split()[:9] for line in first_model if match(pattern_regex_met(chain), line)]

def get_relevant_phe_coordinates(first_model, chain):
    return [line.split()[:9] for line in first_model if match(pattern_regex_phe(chain), line)]

def get_relevant_tyr_coordinates(first_model, chain):
    return [line.split()[:9] for line in first_model if match(pattern_regex_tyr(chain), line)]

def get_relevant_trp_coordinates(first_model, chain):
    return [line.split()[:9] for line in first_model if match(pattern_regex_trp(chain), line)]
