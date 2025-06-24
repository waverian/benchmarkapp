__all__ = ['bench_mark', 'ios_orientation', 'keyboard', 'lang', 'patch_plyer_filechooser']

import os
from os.path import join
from os.path import dirname, abspath
import sys
import _version

# Fix for frozen libs required for windows packaging
import app

historical_path = os.path.abspath(f'{dirname(_version.__file__)}/data/historical_benchmarks')


module_path = abspath(join(dirname(app.__file__),  'uix', 'screens'))
# print(module_path)
sys.path.insert(0, module_path)

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivy.uix.screenmanager import ScreenManager, Screen, ScreenManagerException
from kivy.utils import platform
from kivy.config import Config
from kivy.logger import Logger
from kivy.metrics import dp
from plyer import cpu
from plyer import sysinfo

if platform == 'ios':
    from pyobjus import autoclass
    UIApplication = autoclass('UIApplication')


CPU = cpu
CPUFEATURES = []
for x in CPU.features:
    x1 = x.lower()
    if x1 in CPUFEATURES:
        continue
    for y in ('avx', 'mmx', 'amx', 'vnni', 'arm', 'neon', 'sve'):
        if y in x1:
            CPUFEATURES.append(x1)

try:
    DEVICE = sysinfo.model_info()
except NotImplementedError:
    DEVICE= 'Unknown'

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
    currentDevice = UIDevice.currentDevice()
    iPhone = currentDevice.userInterfaceIdiom == 0
    iPad = currentDevice.userInterfaceIdiom == 1
    sharedApplication = UIApplication.sharedApplication()
    NSProcessInfo = autoclass('NSProcessInfo')
    processInfo = NSProcessInfo.processInfo()
    os_version = processInfo.operatingSystemVersionString.cString().decode('utf-8')

OSNAME = platform_name + ' ' +   os_version

def copy_to_clipboard(text):
    if not text:
        return
    from kivy.core.clipboard import Clipboard
    try:
        Clipboard.copy(str(text))
        make_toast('Copied to clipboard.')
    except JavaException as e:
        make_toast('Error:', e)

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

    if app.navigation_manager.current != 'MainScreen':
        load_screen('MainScreen')
        return

    carousel = app.mainscreen.ids.tcarousel
    if carousel.current_tab.text == 'Benchmark':
        pause_app()
        return

    carousel.switch_to(carousel.tab_list[-1])

def get_formatted_result(result, get_zip=None):
    app = App.get_running_app()
    user_data_dir = app.user_data_dir
    # if result is from main benchmark
    if result == app.result and not app._result_instance:
        # if benchmark is not run, simply return with None
        return None

    # if results.txt exists,  delete it
    # Print result using benchmark c lib
    txt_path = f'{user_data_dir}/results.txt'
    if app.result == result:
        # remove file if it exists
        app._result_instance.print_results_text(txt_path)

        data = None
        with open(os.path.abspath(txt_path), 'r', errors='replace') as f:
            data = f.read()
        if not data:
            return None
        ndata = _replace_text(data)
    else:
        filename = result['filename'].replace('.json', '.txt')

        pfilename = historical_path + '/Results-MP-v3.3/'+ os.sep + filename

        with open(pfilename, 'r', errors='replace') as f:
            ndata = f.read()

        ndata = f'filename - {filename}\n{ndata}'

    if get_zip:
        zip_path = _create_sharable_file(ndata, get_zip)
        ndata = zip_path

    return ndata

def _create_sharable_file(data, get_zip='.zip'):
    app = App.get_running_app()
    user_data_dir = app.user_data_dir
    # data is already edited,
    # Save data to results.txt
    filename = 'results.txt'
    historical = False

    # from pudb import set_trace; set_trace()
    if data.startswith('filename - '):
        historical = True
        fenter_pos = data.find('\n')
        filename = data[:fenter_pos]
        data = data[fenter_pos+1:]
        filename = filename.replace('filename - ', '')


    txt_path = f'{user_data_dir}/{filename}'
    with open(txt_path, 'w', encoding="utf-8") as f:
        f.write(data)

    if get_zip == '.txt':
        return txt_path

    # Get Html from c lib.
    html_path = txt_path.replace('.txt', '.html')
    html = ''
    if not historical:
        app._result_instance.print_results_html(html_path)
        f = open(html_path, 'r', errors='replace')
        html = _edit_html(f.read())
    else:
        with open(f'{historical_path}/Results-MP-v3.3/{filename.replace(".txt", ".html")}', 'r', errors='replace') as f:
            html = f.read()

    # Save html to results.html
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    if get_zip == '.html':
        return html_path

    # Create a zip file with results.txt and results.html
    # Return path of zip file
    zip_path = f'{user_data_dir}/results.zip'

    # Create zip file
    import zipfile
    with zipfile.ZipFile(zip_path, 'w') as z:
        z.write(txt_path, 'results.txt')
        z.write(html_path, 'results.html')
    return zip_path

def _edit_html(data):
    '''data is html text
    '''
    # from pudb import set_trace; set_trace()
    app = App.get_running_app()
    ndata = ''
    nxt_line = False
    for line in data.split('\n'):
        if nxt_line:
            line = nxt_line
            nxt_line = False
        if 'cpu name' in line.lower():
            line2 = line[:].lower()
            line2 = line2.replace('cpu name', 'Model ID')
            ndata += f'{line2}\n' +f'			<td colspan="4">{DEVICE}</td></tr><tr>\n'

            nxt_line = f'			<td colspan="4">{CPU.name}-{CPU.architecture}</td>'
        if 'Waverian lib' in line:
            line = line.replace('Waverian lib', 'Waverian Evolution Benchmark')
        if 'comment' in line.lower():
            txt = app.mainscreen.ids.benchmark_screen.\
                children[0].ids.results.ids.details.ids.ti_comment.text
            txt = txt or ''#f'{OSNAME}-{OSVERSION}'
            nxt_line = f'			<td colspan="4">{ txt}</td>'

        ndata += line + '\n'
    return ndata

def _replace_text(data):
    # Read text,  replace item.
    # Return it's text.
    app = App.get_running_app()
    ndata = ''
    for line in data.split('\n'):
        if line.lower().startswith('cpu name'):
            # Add device ID
            line2 = line[:].lower()
            line2 = line2.replace('cpu name', 'Model ID')
            x = line2.split('-')
            x[-1] = f' {DEVICE}'
            line2 = '-'.join(x)
            ndata += f'{line2}\n'
            # Replace CPU Name
            x = line.split('-')
            x[1] = f' {CPU.name}-{CPU.architecture}'
            line = '-'.join(x)
        if line.lower().startswith('comment'):
            x = line.split('-')
            if x[1].strip() == '':
                txt = app.mainscreen.ids.benchmark_screen.\
                    children[0].ids.results.ids.details.ids.ti_comment.text
                x[1] = txt or ''#f'{OSNAME}-{OSVERSION}'
                line = '- '.join(x)
        ndata += line + '\n'
    return ndata

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

def do_share_ios(data, title, filename=None):
    from plyer import share

    filename = filename or 'results.txt'
    if os.path.exists(data):
        # this is a path to a file
        # Read it and share it's data
        filename = os.path.basename(data)
        with open(data, 'rb') as ifile:
            data = ifile.read()

    share.share_file(
        data, filename, title,
        size=(dp(32), dp(32)), pos=(Window.width - dp(100), dp(300)))

def do_share(path, title, filename=None):
    if platform == 'ios':
        do_share_ios(path, title=None, filename=filename)
    if platform == 'android':
        do_share_android(path, title, file_name=filename)
    return

def do_share_android(filename, title, file_name=None):
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
        user_data_dir = app.user_data_dir
        ldir = user_data_dir

        ss = SharedStorage()
        if ss:
            edir = ss.get_cache_dir()
            if edir and not os.path.exists(edir):
                edir = None

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

    app = App.get_running_app()

    global safe_areas
    safe_areas = ios.get_safe_area()
    # print(safe_areas, 'safe_areas')
    # print(app.rotation, 'rotation')
    safe_areas_ = [safe_areas[x] for x in safe_areas.keys() if safe_areas[x]]
    Logger.debug(f'WaverianApp: iOS: Safe Srea:{safe_areas_} {sharedApplication.statusBarOrientation}')

    # has_notch = bool(NotchDetector.hasTopNotch())
    # has_notch = bool(has_notch or safe_areas)
    has_notch = bool(safe_areas_)
    Logger.debug(f'WaverianApp: Device has notch : {has_notch}')
    return has_notch

def show_status_bar(resuming=False):
    if platform != 'ios':
        return
    # print(sharedApplication.statusBarStyle, 'Style')
    # print(sharedApplication.isStatusBarHidden(), 'is_hidden')
    sharedApplication.setStatusBarStyle_(0)
    sharedApplication.setStatusBarHidden_(0)
    # print(sharedApplication.isStatusBarHidden(), 'is_hidden')
    # print(sharedApplication.isStatusBarHidden(), 'is_hidden')
    sharedApplication.setStatusBarHidden_withAnimation_(False, 1)
    # sharedApplication.keyWindow.rootViewController().prefferStatusBarHidden
    Clock.schedule_once(lambda dt: sharedApplication.setStatusBarStyle_(1), .9 if resuming else -1)

    # print(dir(sharedApplication))
    #.statusBarView_.backgroundColor = UIColor.black

def load_screen(
    screen:Screen, manager:ScreenManager=None,
    store_back:bool=True, kwargs:dict={}, direction='left', load_only=False):
    '''Load the provided screen:
    arguments::
        `screen`: is the name of the screen to be loaded
        `manager`: the manager to load this screen, this defaults to
        the main class.
    '''
    app = App.get_running_app()
    store_back = False if screen == 'StartupScreen' else store_back
    # print(f'manager {manager}')
    manager = manager or app.navigation_manager
    # load screen modules dynamically
    # for example load_screen('LoginScreen')
    # will look for uix/screens/loginscreen
    # load LoginScreen
    module_path = screen.lower()
    if not hasattr(app, module_path):
        import importlib as imp
        module = __import__(module_path)
        screen_class = getattr(module, screen)
        sc = screen_class(**kwargs)
        sc.from_back = not store_back
        sc.name = sc.__class__.__name__
        setattr(app, module_path, sc)
        manager.add_widget(sc)
    else:
        sc = getattr(app, module_path)

    sc.from_back = not store_back

    if load_only:
        return getattr(app, module_path)

    try:
        manager.switch_to(sc, direction=direction)
    except ScreenManagerException as err:
        # from pudb import set_trace; set_trace()
        if sc.manager: sc.manager.remove_widget(sc)
        sc.manager = None
        manager.switch_to(sc, direction=direction)

    if store_back:
        app._navigation_higherarchy.append([sc, manager])

    return getattr(app, module_path)

def read_historical_data(force_reload=False, show_all=False):
    app = App.get_running_app()
    if hasattr(app, '_historical_data') and not force_reload:
        return app._historical_data

    # Load data from disk
    majorgen_path = "Results-MP-v3.3-majorgen"
    norm_path = "Results-MP-v3.3"
    path_to_data = historical_path + f'/{norm_path if show_all else majorgen_path}'
    # majorgen_path = historical_path + f'/{majorgen_path}'
    data = []
    # print(path_to_data)
    # majorgen_files = os.listdir(majorgen_path) 
    for file in os.listdir(path_to_data):
        # print(file)
        if not file.endswith('.json'):
            continue
        import json
        import re
        try:
            with open(join(path_to_data, file)) as fl:
                txt = fl.read()
                txt = re.sub(r'[\uD800-\uDFFF]','?', txt)
                item = json.loads(txt)
                item['filename'] = file
                item['major_gen'] = not show_all
            data.append(item)
        except Exception as err:
            Logger.debug(f'Error reading file {file} for historical path, {path_to_data}')
            Logger.debug(f'Error: {err}')
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
    with open(f'{historical_path}/../museum/museum_data.json') as file:
        jsondata = file.read()

    import json
    app.museum_data = data = json.loads(jsondata)
    return data

def save_data(path):
    from plyer import filechooser
    from datetime import datetime

    def on_save_file_selected(file_path):
        if not file_path:
            return

        # copy the file to the selected location
        # and make a toast

        with open(path, 'rb') as f:
            data = f.read()
            with open(file_path[0], 'wb') as fl:
                fl.write(data)
        make_toast(f'Writtent to {file_path[0]}')

    timestamp = datetime.now().strftime("result-%y-%m-%d-%H-%M")
    default_path = os.path.join(os.path.expanduser("~"), (timestamp + '.' + path.split('.')[-1]))
    filters = {
        '.zip': ["Zip file (*.zip)", "*.zip"],
        '.txt': ["Text file (*.txt)", "*.txt"],
        'html': ["HTML file (*.html)", "*.html"],
        }[path[-4:]]

    filechooser.save_file(
        on_selection=on_save_file_selected,
        path=default_path,
        filters=[filters])

@mainthread
def disable_ios_sleep():
    UIApplication.sharedApplication().idleTimerDisabled = True

@mainthread
def enable_ios_sleep():
    UIApplication.sharedApplication().idleTimerDisabled = False
