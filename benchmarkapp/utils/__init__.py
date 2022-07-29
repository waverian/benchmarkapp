from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import Config
from kivy.logger import Logger
from kivy.metrics import dp
from plyer import cpu
from plyer import devicename

CPU = cpu
CPUFEATURES = []
for x in CPU.features:
    x1 = x.lower()
    if x1 in ('avx', 'mmx', 'amx', 'vnni', 'arm', 'neon', 'sve') and x1 not in CPUFEATURES:
        CPUFEATURES.append(x1)

DEVICE = devicename.device_name

is_desktop = Config.get('kivy', 'desktop') == '1'

import os
import sys
from os.path import join

import platform as pyplatform
from kivy.utils import platform


os_version = pyplatform.release()
OSVERSION = pyplatform.version()

if platform.startswith('win'):
    platform_name = 'Windows'
elif platform.startswith('mac'):
    platform_name = 'macOS'
    mv = pyplatform.mac_ver()
    os_version = f'{mv[0]}'
elif platform == 'linux':
    platform_name = 'Linux'
elif platform == 'android':
    # OSVERISON = cpu._get_prop('ro.product.build.version.release_or_codename')
    platform_name = 'Android'
    #TODO: Move to plyer upstream
    os_version = cpu._get_prop('ro.build.version.release')
    OSVERSION = pyplatform.release()
    
    from jnius import autoclass, cast, JavaException
    JS = autoclass('java.lang.String')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    pm = autoclass('android.content.pm.PackageManager')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
elif platform == 'ios':
    platform_name = 'iOS'
    import ios
    from pyobjus import autoclass
    from pyobjus.objc_py_types import NSSize, NSRect, NSPoint
    UIApplication = autoclass('UIApplication')
    UIDevice = autoclass('UIDevice')
    sharedApplication = UIApplication.sharedApplication()
    NSProcessInfo = autoclass('NSProcessInfo')
    processInfo = NSProcessInfo.processInfo()
    os_version = processInfo.operatingSystemVersionString.cString().decode('utf-8')




OSNAME = platform_name + ' ' +   os_version

def get_system_env():
    # fix env
    env = dict(os.environ)
    if hasattr(sys, '_MEIPASS'): # in pyinstaller binary?
        env = dict(os.environ) # make copy
        lp_key = 'LD_LIBRARY_PATH'
        lp_orig = env.get(lp_key + '_ORIG')
        if lp_orig is not None: # restore original path
            env[lp_key] = lp_orig
        else: # if 
            env.pop(lp_key, None)
    return env

    

def add_device_details_to_result(result):
    app = App.get_running_app()
    app.result['Device Details'] = {
        'OS Name': OSNAME,
        'Kernel Version': OSVERSION,
        'CPU Name': CPU.name,
        'CPU Arch': CPU.architecture,
        'CPU FEATURES': CPUFEATURES,
        }
    for ridx in range(4):
        kernel_results = app.results[ridx]["kernel_results"]
        for idx, key in enumerate([
                'Hydro fragment', 'ICCG excerpt', 'Inner product', 
                'Banded linear equations', 'Tri-diagonal elim, below diagonal',
                'General linear recurrence equations', 'Equation of state fragment',
                'ADI integrationt', 'Integrate predictors', 'Difference predictors',
                'First sum', 'First difference', '2-D PIC (Particle In Cell)',
                '1-D PIC (Particle In Cell)t', 'Casual Fortran. Development version',
                'Monte Carlo search loop', 'Implicit, conditional computation',
                '2-D explicit hydrodynamics fragment', 'General linear recurrence equations',
                'Discrete ordinates transport conditional recurrence', 'Matrix*matrix product',
                'Planckian distribution', '2-D implicit hydrodynamics fragment',
                'Find location of first minimum in array']):
            app.result['results'][ridx][key] = kernel_results[idx]

def pause_app():
    '''
    '''
    if platform == 'android':
        currentActivity = cast(
            'android.app.Activity', PythonActivity.mActivity)
        currentActivity.moveTaskToBack(True)
    else:
        app = App.get_running_app()
        app.stop()

def go_back_in_history(ScreenName:str = None):
    '''Function: Go back in history
    args:

        Screen Name: String: name of Screen to go back
    '''
    app = App.get_running_app()
    if not app:
        return

    carousel = app.root.ids.tcarousel
    if carousel.current_tab.text == 'Benchmark':
        pause_app()
        return

    carousel.switch_to(carousel.tab_list[-1])

def get_formatted_result(result):
    results = result['results']
    import __main__

    txt_result = f'''
Device Details:
===============

OS Name               -  {OSNAME}
Kernel Version        -  {OSVERSION}
CPU Name              -  {CPU.name}
CPU Arch              -  {CPU.architecture}
CPU FEATURES          -  {CPUFEATURES}


Benchmark Details
=================

Benchmark Version     -  {result['version']},
App Version           -  {__main__.__version__},
Date                  -  {result['date']},
Compiler              -  {result['compiler']},
Core Count            -  {result['core_count']},
Singlecore Results    -  {result['singlecore_results']},
Multicore Results     -  {result['multicore_results']},


Detailed Results
================

 --------------------------------------------------------------------
|                |      Non-Optimized      |        Optimized        |
|--------------------------------------------------------------------
|     MFLOPS     | Singlecore | Multicore  | Singlecore | Multicore  |
 --------------------------------------------------------------------'''

    snm = []
    for x in ('maximum', 'average', 'geometric', 'harmonic', 'minimum'):
        for item in results:
            snm.append(
                str(int(item[x])).rjust(12))

    txt_result += '''
|        Maximum |{}|{}|{}|{}|
|        Average |{}|{}|{}|{}|
|      Geometric |{}|{}|{}|{}|
|       Harmonic |{}|{}|{}|{}|
|        Minimum |{}|{}|{}|{}|'''.format(*snm)


    txt_result +='''
 --------------------------------------------------------------------
|                         KERNEL RESULTS:                            |
 --------------------------------------------------------------------
|                |      Non-Optimized      |        Optimized        |
|     MFLOPS     | Singlecore | Multicore  | Singlecore | Multicore  |
 --------------------------------------------------------------------
'''
    kr = ''
    kernel_idx = 0
    KERNEL_COUNT = 24

    while kernel_idx < KERNEL_COUNT:
        kr += '|{}|'.format(str(kernel_idx+1).rjust(16))
        for x in range(4):
            kr+= '{}|'.format(str(int(
                results[x]['kernel_results'][kernel_idx])).rjust(12))
        kr += '\n'
        kernel_idx += 1

    txt_result += kr
    txt_result += ''' --------------------------------------------------------------------'''
    
    return txt_result

@mainthread
def make_toast(message:str = '', after_toast=None, timeout=2):
    from kivy.app import App
    app = App.get_running_app()
    from kivy.core.window import Window
    from kivy.animation import Animation
    from kivy.lang import Builder

    if not hasattr(app, 'toast'):
        app.toast = Builder.load_string('''
Button
    background_normal_color: 0, 0, 0, 1
    text: 'Hello World'
    after_toast: None
    size_hint: None, None
    width: dp(200)
    background_normal: 'data/theme/blue/images/but_cylinder.png'
    text_size: self.width - dp(9), None
    halign: 'center'
    size: dp(190), self.texture_size[1] + dp(40)
    on_release:
        from kivy.core.window import Window
        from kivy.animation import Animation
        Animation.cancel_all(root, 'opacity')
        a = Animation(opacity=0, duration=.5)
        a.bind(on_complete=lambda *dt: Window.remove_widget(root))
        Animation.cancel_all(root, 'opacity')
        a.start(root)
    on_parent: if not args[1] and self.after_toast: self.after_toast()
''')

    bread = app.toast
    if bread.parent: bread.parent.remove_widget(bread)
    bread.text = message
    bread.opacity = 0
    bread.after_toast = after_toast or (lambda *args: '')
    Window.add_widget(bread)
    Animation.cancel_all(bread)
    a = Animation(center_y=Window.center[1] , center_x=Window.center[0], opacity=.9, duration=.25)+\
        Animation(opacity=.9,duration=timeout)+\
        Animation(opacity=0, duration=.25)
    a.bind(on_complete=lambda *dt: Window.remove_widget(bread))
    a.start(bread)

def write_data_to_file(data, out_file):
    if os.path.exists(out_file):
        os.remove(out_file)
    with open(out_file, 'w') as ofile:
        ofile.write(data)

def do_share_ios(data, title):
    from plyer import share
    share.share_file(
        data, 'results.txt', title,
        size=(dp(32), dp(32)), pos=(Window.width/2.1, dp(100)))

def do_share(data, title):
    if platform == 'ios':
        do_share_ios(data, title)
    if platform == 'android':
        do_share_android(data, title)
    return

def do_share_android(data, title):
    from android import api_version, mActivity
    from android.permissions import request_permissions, check_permission, \
        Permission
    from androidstorage4kivy import SharedStorage, Chooser, ShareSheet

    dont_gc = None
        
    def on_permissions(permissions, granted):
        if granted[0] != True:
            Logger.debug(f'Permission: {permissions[0]} granted: {granted[0]}')
            from utils import make_toast
            return make_toast('Please allow storage permissions for the app.')

        dont_gc = edir = ldir = None

        app = App.get_running_app()
        ldir = app.user_data_dir

        ss = SharedStorage()
        if ss:
            edir = ss.get_cache_dir()
            if edir and not os.path.exists(edir):
                edir = None
            
        filename = join(edir or ldir, 'results.txt')
        write_data_to_file(data, filename)
        uri = SharedStorage().copy_to_shared(filename) if edir else filename
        ShareSheet().share_file(uri)


    permission = Permission.WRITE_EXTERNAL_STORAGE
    # Android API 29 onwards has mediastore which helps us share file,
    # saved in external storage; without having to ask for permissions.
    # API < 29 we explicitly ask for permissions and based on state of permissions,
    # enable sharing if permissions is granted.
    # This should idealy be replaced with using FileProvider which fascilitates
    # targetted permissions just for the file being shares, after support for it has been included in
    # p4a and buildozer.
    if api_version <29 and not check_permission(permission):
        request_permissions([permission], on_permissions)
    else:
        on_permissions([permission], [True])

        
    
def device_has_notch():
    if platform != 'ios':
        return False

    safe_areas = ios.get_safe_area()
    safe_areas = [safe_areas[x] for x in safe_areas.keys() if safe_areas[x]]
    Logger.debug(f'WaverianApp: iOS: Safe Srea:{safe_areas} {sharedApplication.statusBarOrientation}')

    # has_notch = bool(NotchDetector.hasTopNotch())
    # has_notch = bool(has_notch or safe_areas)
    has_notch = bool(safe_areas)
    Logger.debug(f'WaverianApp: Device has notch : {has_notch}')
    return has_notch

def load_screen(
    screen:Screen, manager:ScreenManager=None,
    store_back:bool=True, kwargs:dict={}):
    '''Load the provided screen:
    arguments::
        `screen`: is the name of the screen to be loaded
        `manager`: the manager to load this screen, this defaults to
        the main class.
    '''
    app = App.get_running_app()
    store_back = False if screen == 'StartupScreen' else store_back

    manager = manager or app.navigation_manager
    # load screen modules dynamically
    # for example load_screen('LoginScreen')
    # will look for uix/screens/loginscreen
    # load LoginScreen
    module_path = screen.lower()
    if not hasattr(app, module_path):
        import imp
        module = imp.load_module(screen, *imp.find_module(module_path))
        screen_class = getattr(module, screen)
        sc = screen_class(**kwargs)
        sc.from_back = not store_back
        setattr(app, module_path, sc)
        manager.add_widget(sc)
    else:
        sc = getattr(app, module_path)

    sc.from_back = not store_back

    try:
        manager.switch_to(sc)
    except ScreenManagerException as err:
        if sc.manager: sc.manager.remove_widget(sc)
        sc.manager = None
        manager.switch_to(sc)


    if store_back:
        app._navigation_higherarchy.append([sc, manager])

    return getattr(app, module_path)

def read_historical_data(force_reload=False):
    app = App.get_running_app()
    if hasattr(app, '_historical_data') and not force_reload:
        return app._historical_data

    # Load data from disk
    path_to_data = os.path.dirname(__file__) + '/../data/historical_benchmarks/'
    data = []
    for file in os.listdir(path_to_data):
        if not file.endswith('.json'):
            continue
        import json
        try:
            with open(join(path_to_data, file)) as fl:
                item = json.loads(fl.read())
            data.append({
                'System': item['System'],
                'SINGLECORE RESULT': float(item['SINGLECORE RESULT']),
                'MULTICORE RESULT': float(item['MULTICORE RESULT']),
                })
        except Exception as err:
            print(err)
            continue
    return data

def read_museum_data(force_reload=False):
    '''Returns a json of data along with image
    '''
    app = App.get_running_app()
    if hasattr(app, '_museum_data') and not force_reload:
        return app._museum_data

    # Load data from disk
    jsondata = []
    with open(os.path.dirname(__file__) + '/../data/museum/museum_data.json') as file:
        jsondata = file.read()

    import json
    app.museum_data = data = json.loads(jsondata)
    return data

def save_data(data):
    from plyer import filechooser
    from datetime import datetime

    def on_save_file_selected(file_path):
        if not file_path:
            return

        with open(file_path[0], 'w') as ofile:
            ofile.write(data)
        make_toast(f'Writtent to {file_path[0]}')
    
    timestamp = datetime.now().strftime("result-%y-%m-%d-%H-%M.txt")
    default_path = os.path.join(os.path.expanduser("~"), timestamp)
    filechooser.save_file(
        on_selection=on_save_file_selected,
        path=default_path,
        filters=[["Text file (*.txt)", "*.txt"]])
