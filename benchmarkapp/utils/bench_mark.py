'''
'''
import threading
import ctypes
import time

from kivy.app import App

app = App.get_running_app()

from kivy.clock import Clock, mainthread
from kivy.config import Config
from kivy.logger import Logger

is_desktop = Config.get('kivy', 'desktop') == '1'
from kivy.utils import platform

if platform == 'ios':
    from pyobjus import autoclass
    NSString = autoclass('NSString')


def callback(progress, message)->None:
    app.progress = progress
    try:
        message = message.decode('utf-8')
    except AttributeError:
        pass
    app.progress_message = message

@mainthread
def update_result(result):
    app.result = result

try:
    import lfkbenchmark
    lfkbenchmark.callback_func = callback
    benchmark = lfkbenchmark.Benchmark()
except Exception as err:
    callback(0, repr(err))
    Logger.debug(err)


class thread_with_exception(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        result = benchmark.run_benchmark()
        Clock.schedule_once(lambda dt: update_result(result))
        app._benchmark_running = False

    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        Logger.debug('Raising Exception')
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id),
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

def start_benchmark():
    # Start benchmark

    import threading
    t = thread_with_exception('Benchmark Thread')
    t.daemon = True
    t.start()
    return t

def get_results():
    def _get_results():
        try:
            benchmark._setup_benchmark()
            result = benchmark._get_results()
            Clock.schedule_once(lambda dt: update_result(result))
        except Exception as err:
            callback(0, repr(err))
            Logger.debug(err)

    t = threading.Thread(target=_get_results)
    t.daemon = True
    t.start()
