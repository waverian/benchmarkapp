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
import datetime
import json
from typing import Dict, Any, TypeVar

kernel_start_key = None
core_result = {
    'valid': 0,
    'score': 0.0,
    'ratio': 0.0,
    'maximum': 0.0,
    'average': 0.0,
    'geometric': 0.0,
    'harmonic': 0.0,
    'minimum': 0.0,
    'kernels': [0.0,]*24}
''' Single/Multi/Quad Core results
'''

optimized = 'non_optimized'

default_result = {
    'system_info':
        {
        'compiler_info': 'uninitialised',
        'version_info': '0.0.0',
        'cpu_name': 'Uninitialised',
        'cpu_core_count': 0,
        },
    'timestamp': datetime.datetime.now().date().isoformat(),
    'comment': '',
    'full_result':
        {
        'non_optimized':
            {
            'score': 0.0,
            'detailed':
                {
                'single_core': core_result,
                'multi_core': core_result,
                'quad_core': core_result,
                'workstation': core_result,
                },
            },
        'optimized':
            {
            'score': 0.0,
            'detailed':
                {
                'single_core': core_result,
                'multi_core': core_result,
                'quad_core': core_result,
                'workstation': core_result,
                },
            },
        }
    }

def convert_to_json_from_dir(path_to_target):
    # from pudb import set_trace; set_trace()
    for file in os.listdir(path_to_target):
        if file.startswith('lfk3-') and file.endswith('.txt'):

            print(f'Converting: {file}')
            result = convert_to_json_from_file(os.path.join(path_to_target,file))
            print(f'Converted successfully.')
            filename = os.path.join(path_to_target, file.split('.')[0] + '.json')
            with open(filename, 'w', errors='surrogateescape') as ofile:
                ofile.write(result)
                print(f'Written to {filename}\n')

KeyType = TypeVar('KeyType')

def deep_update(mapping: Dict[KeyType, Any], *updating_mappings: Dict[KeyType, Any]) -> Dict[KeyType, Any]:
    updated_mapping = mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping

def convert_to_json_from_file(path_to_target):
    global optimized

    def get_last_string(string, okey=None):
        splits = string.split('-', 1)
        key = splits[0].strip()
        val = splits[-1].strip()
        if okey != None:
            key = okey
        return key, val

    def reset_kernels(return_json, optimized='non_optimized'):
        for core in ('single_core', 'multi_core', 'quad_core', 'workstation'):
            return_json['full_result'][optimized]['detailed'][core]['kernels'] = [0.0,]*24


    def get_core_results(string ,return_json):
        splits = string.split('|', 2)
        key = splits[1].strip().lower()
        # print(key)
        # from pudb import set_trace; set_trace()
        val_splits = [x.strip() for x in splits[2].split('|') if x]

        try:
            float(key)
            # kernels
            global kernel_start_key
            if kernel_start_key is None:
                kernel_start_key = int(key)
                reset_kernels(return_json, optimized=optimized)

            minus = 0 if kernel_start_key == 0 else 1
            kidx = int(key)-minus
            skernels = return_json['full_result'][optimized]['detailed']['single_core']['kernels']
            skernels[kidx] = float(val_splits[0])
            mkernels = return_json['full_result'][optimized]['detailed']['multi_core']['kernels']
            mkernels[kidx] = float(val_splits[1])
            qkernels = return_json['full_result'][optimized]['detailed']['quad_core']['kernels']
            qkernels[kidx] = float(val_splits[2])
            wkernels = return_json['full_result'][optimized]['detailed']['workstation']['kernels']
            try:
                wkernels[kidx] = float(val_splits[3])
            except IndexError:
                pass
            # print(val_splits[0], val_splits[1], val_splits[2])
            # from pudb import set_trace; set_trace()
            # print('Kernels:', skernels[kidx], mkernels[kidx], qkernels[kidx])
            if kidx == 23:
                kernel_start_key = None
            return {
            'full_result': {
                optimized: {
                    'detailed': {
                        'single_core': {'kernels': skernels},
                        'multi_core': {'kernels': mkernels},
                        'quad_core': {'kernels': qkernels},
                        'workstation': {'kernels': wkernels}}}}}
        except ValueError:
            single_core_score = float(val_splits[0])
            multi_core_score = float(val_splits[1])
            quad_core_score = float(val_splits[2])
            workstation_score = None
            try:
                workstation_score = float(val_splits[3])
            except IndexError:
                pass
            nkey = {
                'full_result': {
                    optimized: {
                        'detailed': {
                            'single_core': {key: single_core_score},
                            'multi_core': {key: multi_core_score},
                            'quad_core': {key: quad_core_score},
                            'workstation': {key: workstation_score}}}}}

            if key == 'geometric':
                # from pudb import set_trace; set_trace()
                mkey = {
                    'full_result': {
                        optimized: {
                            'score': (single_core_score * multi_core_score * quad_core_score)**(1/3),
                            'detailed': {
                                'single_core': {"valid": 1, "score": single_core_score,},
                                'multi_core': {"valid": 1, "score": multi_core_score, "ratio": multi_core_score/single_core_score},
                                'quad_core': {"valid": 1, "score": quad_core_score, "ratio": quad_core_score/single_core_score},
                                }}}}
                if workstation_score:
                    mkey['full_result'][optimized]['detailed']['workstation'] = {
                        "valid": 1,
                        "score": workstation_score,
                        "ratio": workstation_score/single_core_score}
                nkey = deep_update(nkey, mkey)
            return nkey

    detect_dict = {
        'Version': ({
            'system_info': {
                'version_info': ''}}, get_last_string),
        'Date': ({
            'timestamp': ''}, get_last_string),
        'Compiler': ({
            'system_info': {
                'compiler_info': ''}}, get_last_string),
        'Core count': ({
            'system_info': {
                'cpu_core_count': ''}}, get_last_string),
        'Logical cores': ({
            'system_info': {
                'cpu_core_count': ''}}, get_last_string),
        'CPU name': ({
            'system_info': {
                'cpu_name': ''}}, get_last_string),
        'Comment': ({
            'comment': ''}, get_last_string),
        'OVERALL RESULT': ({
            'full_result': {
                '<optimized>': {
                    'score': ''}}}, get_last_string),
        'SINGLECORE RESULT': ({
            'full_result': {
                '<optimized>': {
                    'detailed':{
                        'single_core': {'valid': 1, 'score': ''}
                        }}}}, get_last_string),
        'MULTICORE RESULT': ({
            'full_result': {
                '<optimized>': {
                    'detailed':{
                        'multi_core':  {'valid': 1, 'score': '', 'ratio': '<ratio>'}
                        }}}}, get_last_string),
        'QUADCORE RESULT': ({
            'full_result': {
                '<optimized>': {
                    'detailed':{
                        'quad_core':  {'valid': 1, 'score': '', 'ratio': '<ratio>'}
                        }}}}, get_last_string),
        'WORKSTATION RESULT': ({
            'full_result': {
                '<optimized>': {
                    'detailed':{
                        'workstation': {'valid': 1, 'score': '', 'ratio': '<ratio>'}
                        }}}}, get_last_string),
        'Maximum': get_core_results,
        'Average': get_core_results,
        'Geometric': get_core_results,
        'Harmonic': get_core_results,
        'Minimum': get_core_results,
        '0': get_core_results,
        '1': get_core_results,
        '2': get_core_results,
        '3': get_core_results,
        '4': get_core_results,
        '5': get_core_results,
        '6': get_core_results,
        '7': get_core_results,
        '8': get_core_results,
        '9': get_core_results,
        '10': get_core_results,
        '11': get_core_results,
        '12': get_core_results,
        '13': get_core_results,
        '14': get_core_results,
        '15': get_core_results,
        '15': get_core_results,
        '16': get_core_results,
        '17': get_core_results,
        '18': get_core_results,
        '19': get_core_results,
        '20': get_core_results,
        '21': get_core_results,
        '22': get_core_results,
        '23': get_core_results,
        '24': get_core_results,
        }

    return_json = dict(default_result)
    return_json['system_info']['System'] = path_to_target.split(os.sep)[-1].split('.')[0].split('-', 1)[1]

    import __main__
    if os.path.isfile(path_to_target):
        try:
            data = open(path_to_target, 'r', errors='surrogateescape').read()
            for line in data.split('\n'):
                if 'Non-Optimized' in line or 'Non optimized' in line:
                    __main__.optimized = 'non_optimized'
                    continue
                elif 'Optimized' in line:
                    __main__.optimized = 'optimized'
                    continue

                lkey = None
                try:
                    lkey = line.split('|')
                    if lkey:
                        lkey = lkey[1].strip()
                except IndexError:
                    pass

                for key in detect_dict.keys():
                    if line.startswith(key) or lkey and lkey == key:
                        func = detect_dict[key]
                        okey = None
                        if type(func) == tuple:
                            okey = func[0]
                            func = func[1]
                            nkey, val = func(line, okey=okey)
                            # from pudb import set_trace; set_trace()
                            val = val.replace('"', '\\"')
                            try:
                                float(val)
                                sval = f'{val}'
                            except ValueError:
                                sval = f'"{val}"'
                            x = json.dumps(nkey)\
                                .replace('""', sval)\
                                .replace('"<optimized>"', f'"{optimized}"')
                            if '<ratio>' in x:
                                ratio = float(val)/float(return_json['full_result'][optimized]['detailed']['single_core']['score'])
                                # from pudb import set_trace; set_trace()
                                x = x.replace('"<ratio>"', f'{ratio}')
                            # print(f'processing line {x}')
                            nkey = json.loads(x, strict=False)
                        else:
                            nkey = func(line, return_json)
                        return_json = deep_update(return_json, nkey)

            return json.dumps(return_json, indent=4)
        except Exception as err:
            print(f'Issue processing line {line}')
            raise(err)

if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__, argv=None, help=True, version='0.0.1', options_first=False)
    path_to_target = args['<path_to_benchmark_results_dir_or_file>']
    if os.path.isfile(path_to_target):
        print (convert_to_json_from_file(path_to_target))
    elif os.path.isdir(path_to_target):
        convert_to_json_from_dir(path_to_target)
