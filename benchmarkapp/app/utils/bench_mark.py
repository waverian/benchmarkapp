'''
'''
import threading
import ctypes
import time
import utils

from kivy.app import App

app = App.get_running_app()
benchmark_comment = ''
benchmark_workstation = False

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
    # from pudb import set_trace; set_trace()
    try:
        message = message.decode('utf-8')
    except AttributeError:
        pass
    app.progress_message = message

@mainthread
def update_result(result):
    app.result = result.result
    app._result_instance = result

try:
    import evolution_benchmark as lfkbenchmark
    benchmark = lfkbenchmark.Benchmark()
except Exception as err:
    callback(0, repr(err))
    Logger.debug(err)


class thread_with_exception(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def _before_benchmark(self):
        if platform == 'ios':
            utils.disable_ios_sleep()

    def _after_benchmark(self, result):
        if platform == 'ios':
            utils.enable_ios_sleep()
        Clock.schedule_once(lambda dt: update_result(result))
        app._benchmark_running = False

    def run(self):
        args = {'callback':callback}
        if benchmark_comment:
            args['comment'] = benchmark_comment
        args['workstation'] = benchmark_workstation
        # print('Benchmark arguments, ', args, '<<')

        Clock.schedule_once(lambda dt: self._before_benchmark())
        result = benchmark.run_benchmark(**args)
        Clock.schedule_once(lambda dt: self._after_benchmark(result))

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

def start_benchmark(comment=None, workstation=False):
    # Start benchmark
    global benchmark_comment
    global benchmark_workstation
    benchmark_comment = comment
    benchmark_workstation = workstation
    import threading
    t = thread_with_exception('Benchmark Thread')
    t.daemon = True
    t.start()
    return t

def get_benchmark_info():
    def _get_results():
        try:
            result = benchmark.get_parameters()
            def update_benchmark_info(result):
                result['compiler_info'] = result['compiler_info']
                result['version_info'] = result['version_info']
                result['cpu_name'] = f'{utils.CPU.name}'
                app.result['system_info'] = result

            Clock.schedule_once(lambda dt: update_benchmark_info(result))
        except Exception as err:
            callback(0, repr(err))
            Logger.debug(err)

    t = threading.Thread(target=_get_results)
    t.daemon = True
    t.start()
