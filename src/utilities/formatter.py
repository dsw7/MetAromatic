SIZE_COLUMN = 11
SIZE_HBAR = 75


def header(printer):
    def wrapper(data):
        print()
        string = ''
        for entry in ['ARO', 'POS', 'MET', 'POS', 'NORM', 'MET-THETA', 'MET-PHI']:
            if isinstance(entry, float):
                entry = str(round(entry, SIZE_COLUMN - 6))
            string += entry + ' ' * (SIZE_COLUMN - len(entry))
        print(string)
        print('=' * SIZE_HBAR)
        printer(data)
        print('=' * SIZE_HBAR)
    return wrapper


def custom_pretty_print_single_bridging_interaction(data):
    for row in data:
        string = ''
        for entry in row:
            if isinstance(entry, float):
                entry = str(round(entry, SIZE_COLUMN  - 6))
            string += entry + ' ' * (SIZE_COLUMN  - len(entry))
        print(string)
