'''Turns results from lfk-benchmark-results{}.text into a json file.
Works on multiple files.

results_to_json.

Usage:
  results_to_json <path_to_benchmark_results_dir_or_file>
  results_to_json -h | --help
  results_to_json --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  '''
import os

def convert_to_json_from_dir(path_to_target):
    for file in os.listdir(path_to_target):
        if file.startswith('lfk-') and file.endswith('.txt'):
            
            print(f'Converting: {file}')
            result = convert_to_json_from_file(os.path.join(path_to_target,file))
            print(f'Converted successfully.')
            filename = os.path.join(path_to_target, file.split('.')[0] + '.json')
            with open(filename, 'w') as ofile:
                ofile.write(result)
                print(f'Written to {filename}\n')


def convert_to_json_from_file(path_to_target):

    def get_last_string(string):
        splits = string.split('-', 1)
        key = splits[0].strip()
        val = splits[-1].strip()
        return key, val
    
    def get_core_results(string):
        splits = string.split('|', 2)
        key = splits[1].strip()
        try:
            key = {
            '1': 'Hydro fragment',
            '2': 'ICCG excerpt',
            '3': 'Inner product',
            '4': 'Banded linear equations',
            '5': 'Tri-diagonal elim, below diagonal',
            '6': 'General linear recurrence equations',
            '7': 'Equation of state fragment',
            '8': 'ADI integrationt',
            '9': 'Integrate predictors',
            '10': 'Difference predictors',
            '11': 'First sum',
            '12': 'First difference',
            '13': '2-D PIC (Particle In Cell)',
            '14': '1-D PIC (Particle In Cell)t',
            '15': 'Casual Fortran. Development version',
            '16': 'Monte Carlo search loop',
            '17': 'Implicit, conditional computation',
            '18': '2-D explicit hydrodynamics fragment',
            '19': 'General linear recurrence equations',
            '20': 'Discrete ordinates transport conditional recurrence',
            '21': 'Matrix*matrix product',
            '22': 'Planckian distribution',
            '23': '2-D implicit hydrodynamics fragment',
            '24': 'Find location of first minimum in array'
            }[key]
        except KeyError:
            pass
        
        val_splits = splits[2].split('|')
        return key, {
            'Non-Optimized': {
                'Singlecore': val_splits[0].strip(),
                'Multicore': val_splits[1].strip()},
            'Optimized': {
                'Singlecore': val_splits[2].strip(),
                'Multicore': val_splits[3].strip()}
                }

    detect_dict = {
        'Version': get_last_string,
        'Date': get_last_string,
        'Compiler': get_last_string,
        'Core count': get_last_string,
        'SINGLECORE RESULT': get_last_string,
        'MULTICORE RESULT': get_last_string,
        '|        Maximum': get_core_results,
        '|        Average': get_core_results,
        '|      Geometric': get_core_results,
        '|       Harmonic': get_core_results,
        '|       Miniimum': get_core_results,
        '|              1': get_core_results,
        '|              2': get_core_results,
        '|              3': get_core_results,
        '|              4': get_core_results,
        '|              5': get_core_results,
        '|              6': get_core_results,
        '|              7': get_core_results,
        '|              8': get_core_results,
        '|              9': get_core_results,
        '|             10': get_core_results,
        '|             11': get_core_results,
        '|             12': get_core_results,
        '|             13': get_core_results,
        '|             14': get_core_results,
        '|             15': get_core_results,
        '|             15': get_core_results,
        '|             16': get_core_results,
        '|             17': get_core_results,
        '|             18': get_core_results,
        '|             19': get_core_results,
        '|             20': get_core_results,
        '|             21': get_core_results,
        '|             22': get_core_results,
        '|             23': get_core_results,
        '|             24': get_core_results,
        }

    return_json = {
        'System': path_to_target.split(os.sep)[-1].split('.')[0].split('-', 1)[1],}

    if os.path.isfile(path_to_target):
        try:
            data = open(path_to_target, 'r').read()

            for line in data.split('\n'):
                for key in detect_dict.keys():
                    if line.startswith(key):
                        nkey, val = detect_dict[key](line)
                        return_json[nkey] = val

            import json
            return json.dumps(return_json, indent=4)
        except Exception as err:
            print(err)

if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__, argv=None, help=True, version='0.0.1', options_first=False)
    path_to_target = args['<path_to_benchmark_results_dir_or_file>']
    if os.path.isfile(path_to_target):
        print (convert_to_json_from_file(path_to_target))
    elif os.path.isdir(path_to_target):
        convert_to_json_from_dir(path_to_target)
