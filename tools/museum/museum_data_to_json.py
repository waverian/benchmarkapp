'''Turns results from nuseum data into a json file.
Works on multiple files.

results_to_json.

Usage:
  museum_data_to_json <path_to_museum_data>
  museum_data_to_json --reverse <path_to_json>
  museum_data_to_json -h | --help
  museum_data_to_json --version

Options:
  -h --help     Show this screen.
  --version     Show version.

Sample commands:

    Add your files to the dir tools/museum/Apple/... dir
    with the .txt and the .png with exact same name.

    Install Dependencies..

    Make sure to install pillow,  Kivy and a venv and activate that env.

    ```
    python3 -m venv ./venv
    source venv/bin/activate 
    pip install -r tools/build/requiremts.txt
    pip install pillow docopt
    ```

    To make the museum data into a digestable json file and fast loading
     atlas images, run the following command.

    ```
    python3 tools/museum/museum_data_to_json.py tools/museum/museum_data
    ```

    The command above takes the data from tools/museum/museum_data and builds
    museum_data.json and corresponding atlas files for each company.

    That's it now you can run your app and the updated data should show up
    in the museum tab.

    
    The following should almost never be needed!!!
    Only run it if source files are not available for some reason.

    To reverse the process above, run the following command::

    ```
    python3 tools/museum/museum_data_to_json.py --reverse benchmarkapp/data/museum
    ```

    The command above takes the data from benchmarkapp/data/museum parsing the
    museum_data.json and the corresponding atlas files and decouples them to
    the way the original resources were in tools/museum/museum_data

  '''

import os
os.environ['KIVY_NO_ARGS'] = "1"
from os.path import join, isfile, isdir, abspath, dirname
from os import listdir
import json
from PIL import Image
from pathlib import Path
import shutil



script_dir = abspath(dirname(__file__))
root_dir = abspath(script_dir + '/../..')

def _get_image_for_cpu(idx, lsdir, file, filename):
    try:
        # let's figure out image for this cpu
        prev = lsdir[idx - 1]
        image = None
        if prev.lower().startswith(filename.lower()) and\
             prev.endswith(('.jpg', '.png', '.jpeg')):
            image = prev
        else:
            nxt = lsdir[idx + 1]
            if nxt.lower().startswith(filename.lower())\
                 and nxt.endswith(('.jpg', '.png', '.jpeg')):
                image = nxt
            else:
                # from pudb import set_trace; set_trace()
                raise Exception(
                    'Unexpected file/image not found', file, filename, )
    except IndexError:
        print('IndexError', file, prev, prev.startswith(
                file.split('.')[0]), prev.endswith(('.jpg', 'png')))
    return image

def _parse_cpu_details(path_to_file, data):
    print('Processing: ', path_to_file)
    with open(path_to_file) as file:
        content = file.read().split('\n')

    note = False
    for line in content:
        # print(line, '<< line ')
        if note:
            data['Historical Note'] += '\n' + line
            continue
        
        if line.lower().startswith(('historical note', 'historic note')):
            note = True
            data['Historical Note'] = line
            continue
        # print(note, line)
        key, value = line.split(':')
        data[key] = value
    return data

def write_museum_data(path_to_json):
    data_dir = abspath(root_dir + '/benchmarkapp/data/museum')
    target_dir = abspath(root_dir + '/tools/museum/museum_data')
    if not os.path.exists(target_dir): os.mkdir(target_dir)

    json_data = ''
    with open(data_dir + '/museum_data.json') as fp:
        json_data = json.load(fp)


    for cpu_dir in json_data:
        # print(cpu_dir)
        target_cpu_dir = join(target_dir , cpu_dir)
        if not os.path.exists(target_cpu_dir): os.mkdir(target_cpu_dir)
        for cpu_item in json_data[cpu_dir]:
            # print(cpu_item)
            filename = cpu_item + '.txt'
            cpu_item_data = json_data[cpu_dir][cpu_item]
            source_image_filename = cpu_item_data.pop('image')

            data = ''
            for key in cpu_item_data:
                data += f'{key}: {cpu_item_data[key]}\n'

            with open(join(target_cpu_dir, filename), 'w') as fp:
                fp.write(data)

            atlasfile = abspath(f'benchmarkapp/data/museum/{cpu_dir}.atlas')
            
            atlasdata = ''
            with open(atlasfile) as fp:
                atlasdata = fp.read()

            atlasjson = json.loads(atlasdata)
            # from pudb import set_trace; set_trace()
            for img in atlasjson:
                imgfile = f'benchmarkapp/data/museum/{img}'
                atlas_image = Image.open(imgfile)
                imgdata = atlasjson[img]
                try:
                    cpu_img = [x for x in imgdata if x.startswith(cpu_item)][0]
                except IndexError:
                    cpu_img = source_image_filename.split(os.sep)[-1].split('.')[0]
                left, upper, width, height = imgdata[cpu_img]
                imgtosave = atlas_image.transpose(
                    Image.FLIP_TOP_BOTTOM).crop(
                        [left, upper, left+width, upper+height]).transpose(
                            Image.FLIP_TOP_BOTTOM)
                
                imgtosave.save(join(target_cpu_dir, cpu_img + '.png'))


def read_museum_data(path_to_data=None, force_reload=False):
    '''Returns a json of data along with image
    '''
    # Load data from disk
    if not path_to_data:
        path_to_data = abspath(root_dir + '/tools/museum/museum_data')
    else:
        path_to_data = abspath(join(root_dir, path_to_data))
    data = {}
    for directory in os.listdir(path_to_data):
        # File here should list the directories like Apple, Intel, 
        path_to_dir = join(path_to_data, directory)
        if os.path.isfile(path_to_dir) or directory.startswith('.'):
            continue
        lsdir = os.listdir(path_to_dir)
        lsdir = [x for x in lsdir]
        lsdir.sort()
        details = {}
        for idx, file in enumerate(lsdir):
            # print(file)
            if not file.endswith('.txt'):
                continue
            path_to_file = join(path_to_dir, file)
            filename = file.split('.')[0]
            image = _get_image_for_cpu(idx, lsdir, file, filename)

            # print(path_to_file, directory, image)
            details[filename] = _parse_cpu_details(
                path_to_file, {'image': join('data', 'museum', directory, image)})

        data[directory] = details

    import json
    return json.dumps(data, indent=4)

def get_max_size(data_dir, cpu_dir, pngs, target_dir):
    sizes = []
    npngs = []
    npngdir = join(data_dir, cpu_dir, 'truncated')
    pngdir = join(data_dir, cpu_dir)
    target_cpu_dir = join(target_dir, cpu_dir)
    
    try:
        shutil.rmtree(npngdir)
    except FileNotFoundError:
        pass 
    os.mkdir(npngdir)
    try:
        os.mkdir(target_cpu_dir)
    except FileExistsError:
        pass
    
    for png in pngs:
        fl = join(pngdir, png)
        dst = join(target_cpu_dir, png)
        shutil.copyfile(fl, dst)
        img = Image.open(fl)
        w, h = img.size
        max_size = 512
        if w > max_size or h > max_size:
            aspect_ratio = w / h
            if w > h:
                new_width = max_size
                new_height = int(max_size / aspect_ratio)
            else:
                new_height = max_size
                new_width = int(max_size * aspect_ratio)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            w, h = new_width, new_height
        output_path = join(npngdir, png)
        img.save(output_path)
        npngs.append(output_path)
        sizes.append((w, h))

    return sizes, npngs

def can_fit(images, width):
    """Check if all images can fit in a square of width x width."""
    row_width, row_height, total_height = 0, 0, 0
    for img_width, img_height in images:
        if img_width > width:
            return False  # Image too wide for this width
        if row_width + img_width > width:
            total_height += row_height
            row_width, row_height = 0, 0
        row_width += img_width
        row_height = max(row_height, img_height)
    total_height += row_height  # Add the height of the last row
    return total_height <= width

def calculate_max_width(images):
    """Calculate the maximum width to pack images in a WxW resolution."""
    images.sort(key=lambda x: -x[1])  # Sort images by height descending
    low = max(img[0] for img in images)
    high = sum(img[0] for img in images)
    
    while low < high:
        mid = (low + high) // 2
        if can_fit(images, mid):
            high = mid
        else:
            low = mid + 1
    
    return low

def export_museum_data_with_atlas(data):
    data_dir = abspath(root_dir + '/tools/museum/museum_data')
    target_dir = abspath(root_dir + '/benchmarkapp/data/museum')
    if os.path.exists(target_dir):
        # print(f'Dir : {target_dir} exists; backup or delete it.')
        shutil.rmtree(target_dir)
        # print(data)
        # return

    os.mkdir(target_dir)
    # write museum data to disk
    with open(join(target_dir, 'museum_data.json'), 'w') as fp:
        fp.write(data)

    # make the atlas from pngs
    for cpu_dir in os.listdir(data_dir):
        if cpu_dir.startswith('.'):
            continue
        pngs = [x for x in os.listdir(join(data_dir, cpu_dir))\
                 if x.endswith(('.jpg', '.png', '.jpeg'))]
        image_sizes, npngs = get_max_size(data_dir, cpu_dir, pngs, target_dir)
        width = calculate_max_width(image_sizes)
        cur_dir = os.getcwd()
        os.chdir(target_dir)
        from kivy.atlas import Atlas
        Atlas.create(cpu_dir, npngs, width + 200)
        # remove generated dir
        shutil.rmtree(join(data_dir, cpu_dir, 'truncated'))
        # go back to previous dir
        os.chdir(cur_dir)
    print('Data succesfully written to ', target_dir)
    

if __name__ == '__main__':
    from docopt import docopt
    args = docopt(
        __doc__, argv=None, help=True, version='0.0.1', options_first=False)
    path_to_target = args['<path_to_museum_data>']
    path_to_json = args['<path_to_json>']
    if path_to_target:
        data = read_museum_data(path_to_target)
        export_museum_data_with_atlas(data)
    elif path_to_json:
        write_museum_data(path_to_json)