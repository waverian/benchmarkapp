'''Turns results from nuseum data into a json file.
Works on multiple files.

results_to_json.

Usage:
  museum_data_to_json <path_to_museum_data>
  museum_data_to_json -h | --help
  museum_data_to_json --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  '''

import os
from os.path import join, isfile, isdir
from os import listdir

def _get_image_for_cpu(idx, lsdir, file, filename):
    try:
        # let's figure out image for this cpu
        prev = lsdir[idx - 1]
        image = None
        if prev.startswith(filename) and prev.endswith(('.jpg', 'png')):
            image = prev
        else:
            nxt = lsdir[idx + 1]
            if nxt.startswith(filename) and nxt.endswith(('.jpg', 'png')):
                image = nxt
            else:
                raise Exception('Unexpected file/image not found', file, filename, )
    except IndexError:
        # print('IndexError', file, prev, prev.startswith(file.split('.')[0]), prev.endswith(('.jpg', 'png')))
        pass
    return image

def _parse_cpu_details(path_to_file, data):
    with open(path_to_file) as file:
        content = file.read().split('\n')

    note = False
    for line in content:
        if note:
            try:
                data['historical note:'] += '\n' + line
            except KeyError:
                data['historical note:'] = line
            continue
        
        if line.lower().startswith(('historical note', 'historic note')):
            note = True
            continue
        # print(line)
        key, value = line.split(':')
        data[key] = value
    return data

def read_museum_data(path_to_data=None, force_reload=False):
    '''Returns a json of data along with image
    '''
    # Load data from disk
    if not path_to_data:
        path_to_data = os.path.dirname(__file__) + '/../benchmarkapp/data/museum/'
    data = {}
    for directory in os.listdir(path_to_data):
        # File here should list the directories like Apple, Intel, 
        path_to_dir = join(path_to_data, directory)
        if os.path.isfile(path_to_dir) or directory.startswith('.'):
            continue
        lsdir = os.listdir(path_to_dir)
        lsdir = [x.lower() for x in lsdir]
        lsdir.sort()
        details = {}
        for idx, file in enumerate(lsdir):
            print(file)
            if not file.endswith('.txt'):
                continue
            path_to_file = join(path_to_dir, file)
            filename = file.split('.')[0]
            image = _get_image_for_cpu(idx, lsdir, file, filename)

            print(path_to_file, directory, image)
            details[filename] = _parse_cpu_details(
                path_to_file, {'image': join('data', 'museum', directory, image)})

        data[directory] = details

    import json
    data = json.dumps(data, indent=4)
    print(data)

if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__, argv=None, help=True, version='0.0.1', options_first=False)
    path_to_target = args['<path_to_museum_data>']
    # if os.path.isfile(path_to_target):
    read_museum_data(path_to_target)