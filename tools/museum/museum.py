''' Museum Module
'''
__all__ = ['do_museum_md5_sum', 'update_museum_data_to_source_tree']
import os
import hashlib
import zipfile

def zip_directory(directory_path, zip_name):
    # Create a zip file from the directory
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory_path))

def calculate_md5(file_path):
    # Calculate the MD5 checksum of the file
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def do_museum_md5_sum(museum_data_dir):
    # museum_dats dir already checkd for and known to exist.
    zip_name = 'museum_data.zip'

    # Zip the museum_data directory
    zip_directory(museum_data_dir, zip_name)

    # Calculate the MD5 checksum of the zip file
    # from pudb import set_trace; set_trace()
    md5sum = calculate_md5(zip_name)

    os.remove(zip_name)

    return md5sum

def check_museum_imports():
    dependencies = ['PIL']
    for dep in dependencies:
        try:
            module = __import__(dep)
            return True
        except (ImportError, ModuleNotFoundError) as err:
            print(err)
            return False


def update_museum_data_to_source_tree(museum_data_dir):
    if not check_museum_imports():
        return

    # required modules exits
    # now run the command for the 
    from museum_data_to_json import read_museum_data, export_museum_data_with_atlas

    path_to_target = museum_data_dir
    data = read_museum_data(path_to_target)
    export_museum_data_with_atlas(data)

    save_md5sum(museum_data_dir)

def save_md5sum(museum_data_dir):
    nmd5 = do_museum_md5_sum(museum_data_dir)
    with open(os.path.abspath(museum_data_dir + '/../museum.md5'), 'w') as fp:
        fp.write(nmd5)
