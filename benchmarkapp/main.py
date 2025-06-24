'''
'''
import os
import sys
import app

sys.path.append(os.path.dirname(os.path.abspath(app.__file__)))
from env import setup_env

from kivy.logger import Logger
from kivy.app import App

from _version import __version__

def crashed_earlier():
    app = App.get_running_app()
    global crash_marker
    crash_marker = f'{app.user_data_dir}/.benchmarkapp_crashed'
    return os.path.exists(crash_marker)

def run_benchmark_app():
    Logger.debug(f'Benchmark Main: {sys.argv}')
    from app.benchmarkapp import BenchMarkApp
    BenchMarkApp().run()
    return

def do_museum_check():
    museum_path = os.path.join(os.path.dirname(__file__), '../tools/museum')
    if not os.path.exists(museum_path):
        return

    # We are running build/developer mode
    # check md5sum for museum
    sys.path.append(os.path.abspath(museum_path))
    # print(sys.path)
    from museum import do_museum_md5_sum, update_museum_data_to_source_tree

    museum_data_dir = os.path.join(museum_path, 'museum_data')
    if not os.path.exists(museum_data_dir):
        print('Museum data does not seem to exist,  skipping to normal boot')
    else:
        existing_md5sum = ''
        try:
            with open(os.path.join(museum_path, 'museum.md5')) as fp:
                existing_md5sum = fp.read()
        except FileNotFoundError:
            existing_md5sum = do_museum_md5_sum(museum_data_dir)

        nmd5 = do_museum_md5_sum(museum_data_dir)
        if existing_md5sum == nmd5:
            Logger.debug('Museum: Museum data not touched, skipping source tree updation.')
        else:
            print('Md5 sums do not match! Will update the museum data to source tree.')
            update_museum_data_to_source_tree(museum_data_dir)



if __name__ == '__main__':
    if os.environ.get('KIVY_BUILD', '') == '':
        # only run these checks on desktops/builders
        do_museum_check()

    if hasattr(sys, '_MEIPASS'):
        from kivy.resources import resource_add_path
        resource_add_path(os.path.join(sys._MEIPASS))

    try:
        run_benchmark_app()
    except Exception as err:
        Logger.debug(f'BenchmarkApp crashed: err: {err}')
        from pathlib import Path
        app = App.get_running_app()
        crash_marker = f'{app.user_data_dir}/.benchmark_crashed'
        Path(crash_marker).touch()
        print("Unhandled exception:", sys.exc_info()[0])
        raise
