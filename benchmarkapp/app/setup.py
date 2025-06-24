import os
from os.path import dirname, join, abspath
from setuptools import setup, Extension
from setuptools import find_packages

root_dir = abspath(dirname(__file__))
compile_c = False


def find_py_files(directory, exclude_dirs=None):
    """Recursively find all .py files in a directory, excluding specified directories."""
    if exclude_dirs is None:
        exclude_dirs = []
    
    pyx_files = []
    for root, dirs, files in os.walk(directory):
        if any(exclude in root for exclude in exclude_dirs):
            continue
        for file in files:
            if compile_c and file.endswith('.c'):
                file_path = os.path.join(root, os.path.splitext(file)[0]+'.c')
                pyx_files.append(file_path)
            elif compile_c == False and file.endswith('.py'):
                file_path = os.path.join(root, file)
                os.rename(file_path,file_path + 'x')
                pyx_files.append(file_path + 'x')
    return pyx_files

try:
    # Collect all .py files from specified directories excluding 'plyer'
    all_py_files = ['__init__.py', 'benchmarkapp.py', 'compiled_benchmark.py']
    for file in all_py_files:
        os.rename(join(root_dir, file), join(root_dir, file + 'x'))
except FileNotFoundError:
    compile_c = True
    all_py_files =  ['__init__.c', 'benchmarkapp.c', 'compiled_benchmark.c']

extensions = []

# Directories to search for Python files
directories = ['env', 'uix', 'utils']

# Exclude 'plyer' from cythonization
excluded_dirs = ['plyer']

for directory in directories:
    all_py_files += find_py_files(directory, exclude_dirs=excluded_dirs)

for pyfile in all_py_files:
    extensions.append(Extension(
        name = '.'.join(['app'] + os.path.splitext(pyfile)[0].split(os.sep)),
        sources = all_py_files,
        language='c',
        language_level='3',
        cython_directives={
            'language_level': 3
        }))

packages = find_packages(include=['app', 'env', 'uix', "utils"])
# print('packages', packages)


setup(
    name='app',
    description='',
    author='',
    author_email='',
    cmdclass={},
    packages=packages,
    package_dir={'app': 'app'},
    options={
        'bdist_wheel':{'universal':'1'}
    },
    ext_modules=extensions
)