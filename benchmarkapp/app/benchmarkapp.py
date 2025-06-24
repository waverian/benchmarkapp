'''Main module for App entry of Livemore Loops Kivy UI App.
 Copyright (c) Waverian Team 2022.
 License @ https://github.com/waverian/benchmarkapp/tree/main/LICENSE
 '''

import datetime

from kivy.app import App
from kivy.properties import (StringProperty, NumericProperty,
    ObjectProperty, BooleanProperty, DictProperty, OptionProperty, ListProperty)
from kivy.clock import Clock
from kivy.config import Config
from kivy.logger import Logger
from kivy.utils import platform
from kivy.core.window import Window
from kivy.resources import resource_add_path
from kivy.factory import Factory

Factory.register('WaverianScrollView', module='uix.widgets.waverianscroll')
Factory.register('TabbedScreen', module='uix.widgets.tabbed_screen')

from uix.benchmark_results import BenchmarkResults
from uix.widgets.simple_graph import SimpleBarGraph

import os
# os.environ['EVOBENCHTESTMODE'] = '1'
import utils
from utils import make_toast, load_screen, show_status_bar

resource_add_path(os.path.abspath(os.path.dirname(__file__)))

from utils.lang import Lang

global_lang = Lang('en')


class BenchMarkApp(App):
    '''The main purpose of this Kivy App is to create a UI with
    the following elements::
    - Benchmark results screen to display the results of benchmark.
    - Graphs comparing current results with hostorical results.
    - Display Hostorical data about the CPUs & their Architecture
    '''

    pro_mode_text = 'Pro'
    '''
    '''

    title = 'Evolution Benchmark' + ' ' + pro_mode_text
    ''' This is the title that should appear on the app titile bar.
    '''

    icon = 'data/app_icon.png'
    '''Icon that we want to use while app is running.
    '''

    _benchmark_running = BooleanProperty(False)
    '''This signifies if benchmark is running or not.

    `_benchmark_running` is a ~kivy.properties.`BooleanProperty` defaults to `False`
    '''

    font_color_active = ListProperty((108./255., 172./255., 212./255., 1))
    '''We use a White/desaturated textured background png and add color programatically to ease theming.
    Colors are to be provided from 0-1 in OpenGL format thus the devision /255'''

    font_color_bright = ListProperty((14./255., 12./255., 20./255., 1))
    '''
    '''

    font_color_dull = ListProperty((1, 1, 1, 1))
    '''
    '''

    lang = StringProperty('en')
    ''' Get Text encapsulating Language specifier for the whole app.

    `lang` is a ˜.kivy.properties.StringProperty defaults to `en` english language.

    Currently supported languages::

        `en`: `English`
        `ru`: `russian`
        `hi`: `Hindi`
        `uk`: `ukranian`
    '''

    def on_lang(self, instance, lang):
        Config.set('waverianapp', 'language', lang)
        Config.write()
        global_lang.switch_lang(lang)

    museum_data = DictProperty({})
    '''Data to be displayed on the museum tab.

    `museum_data` id a ~.kivy.properties.`DictProperty` defaults to `{}`
    '''

    # navigation_manager = ObjectProperty(None, rebind=True)
    # '''This is the base navigation manager used for loading screens for our app.
    # '''

    selected_item_color = ListProperty((214/255, 1, 1, 1))# (0, 1, 0, 1))
    '''
    '''

    progress = NumericProperty(0)
    '''Benchmark progress. range 0-1 .

     `progress` is a ~kivy.properties.`NumericProperty` defaults to `0`
    '''

    progress_message = StringProperty('')
    '''This is the message sent to us by the benchmark cors c lib.
    `progress_message` is a ~kivy.properties.`StringProperty` defaults to `""`
    '''

    kernel_keys = {
            '1': 'Hydro fragment',
            '2': 'ICCG excerpt (Incomplete Cholesky Conjugate Gradient)',
            '3': 'Inner product',
            '4': 'Banded linear equations',
            '5': 'Tri-diagonal elim, below diagonal',
            '6': 'General linear recurrence equations',
            '7': 'Equation of state fragment',
            '8': 'ADI integrationt',
            '9': 'Integrate predictors',
            '10': 'Difference predictors',
            '11': 'First sum',
            '12': 'First difference',
            '13': '2-D PIC (Particle In Cell)',
            '14': '1-D PIC (Particle In Cell)',
            '15': 'Casual Fortran. Development version',
            '16': 'Monte Carlo search loop',
            '17': 'Implicit, conditional computation',
            '18': '2-D explicit hydrodynamics fragment',
            '19': 'General linear recurrence equations',
            '20': 'Discrete ordinates transport conditional recurrence on XX',
            '21': 'Matrix*matrix product',
            '22': 'Planckian distribution',
            '23': '2-D implicit hydrodynamics fragment',
            '24': 'Find location of first minimum in array'}

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

    _result_instance = None
    '''This points to the result object returned by the benchmark c lib.

    `_result_instance` is a `~Object` defaults to `None`
    '''

    result = DictProperty(default_result)

    '''This is the result updated by the benchmark c lib to be displayed on UI.

    `result` is a ~kivy.properties.`DictProperty` defaults to `{}`
    '''

    theme = StringProperty('blue')
    '''Theme for UI,  default theme is dark background with blue highlight.

    `theme` is a ~kivy.properties.`StringProperty` defaults to `blue`
     '''
    
    primary_color = ListProperty([.184, .184, .184, 1])
    '''
    '''

    rotation = OptionProperty(0, options=(0, 90, 180, 270, 360))
    '''Window Rotation usefull for some ios UI changes according
    to rotation and Status Bar appearance.

    `roation` is a ~kivy.properties.`OptionProperty` defaults to `0`
    '''

    _window_width = NumericProperty('270sp')
    '''This property is updated at most once per second while window width is changing,
    used to make a delayed UI reaction to the change allowing less property dispatches.

    TODO: replace Window.width with this where possible.
     '''

    def build(self):
        name = self.__class__.__name__.lower()
        name = name[:-3] if name.endswith("app") else name
        cname = f'compiled_{name}'
        fname = os.path.join(os.path.dirname(__file__), name + '.kv')
        # print(fname, os.path.exists(fname), '<<')
        root = None
        if not os.path.exists(fname):
            # try and load AppName.py if it exists.
            root = __import__(cname).root


        #self.script_path = script_path)

        # icext = 'ico' if platform == 'win' else 'png'
        # self.icon = f'data/theme/{self.theme}/iconsplash/icon.{icext}'
        # # Here we build our own navigation higherarchy.
        # # So we can decide what to do when the back
        # # button is pressed.
        self._navigation_higherarchy = []

        if root:
            return root


    def on_start(self):
        import os
        self._benchmark_running = False
        self._benchmark_thread = None
        # initialize Benchmark screen
        self._museum = None
        self._about = None

        self._navigation_higherarchy = []
        self.navigation_manager = self.root.ids.manager

        import __main__
        if __main__.crashed_earlier():
            load_screen('LogFileScreen')
            os.remove(__main__.crash_marker)
        else:
            load_screen('MainScreen')

        # bind to the keyboard to listen to
        # specific key codes
        from utils.keyboard import hook_keyboard
        Clock.schedule_once(lambda dt: hook_keyboard())

    #     self.window_width_trigger = Clock.create_trigger(self._update_width, 1/30)
    #     self.window_width_trigger()
    #     Window.bind(width=lambda *args: self.window_width_trigger())

    # def _update_width(self, dt):
    #     self._window_width = Window.width

    def on_resume(self):
        if platform == 'ios':
            # from utils import ios_orientation
            Clock.schedule_once(lambda dt: show_status_bar(resuming=True))
            # ios_orientation.orientation_responder._adjust_for_notch(self.root.rotation)
        self.stop_benchmark()
        return True

    def on_size(self):
        if platform == 'ios':
            show_status_bar()

    def load_about(self, screen, reset=False):
        if not reset and self._about:
            return

        from uix.aboutscreen import AboutScreen
        self._about = about = AboutScreen()
        screen.add_widget(about)


    def load_benchmark_info(self, screen, reset=False):
        if not hasattr(self, 'benchmark_results'):
            self.benchmark_results = BenchmarkResults()
            screen.add_widget(self.benchmark_results)


        from utils import bench_mark
        bench_mark.get_benchmark_info()

    def load_museum(self, screen, reset=False):
        if not reset and self._museum:
            return

        if not self._museum:
            from uix.museum import Museum
            self._museum = Museum()
            screen.add_widget(self._museum)

        utils.read_museum_data()

    def load_charts(self, screen, single_multi, force=False):
        screen = self.mainscreen.ids['charts_single' if single_multi.lower() == 'single' else 'charts_multi']

        if not  hasattr(screen, 'graph') or force:
            screen.clear_widgets()
            screen.graph = graph = SimpleBarGraph()
            screen.add_widget(graph)

            graph.bar_key = lambda d: d['full_result']['non_optimized']['detailed'][single_multi.lower() + '_core']['score']
            graph.title = single_multi.upper() + '_CORE'
            graph.x_axis_title = ''
            graph.y_axis_title = ''
            graph.results = utils.read_historical_data(show_all=False)
        else:
            graph = screen.graph

        # check and update this comp results on graph
        # from pudb import set_trace; set_trace()
        if self.result['full_result'] == self.__class__.default_result['full_result']:
            return

        # benchmark has been run, update graph with results
        bar = graph.ids.this_comp_bar
        # from pudb import set_trace; set_trace()
        score = str(int(
            self.result['full_result']['non_optimized']
                ['detailed']['single_core' if single_multi == 'single' else 'multi_core']['score']))

        bar.text = '_'.join([
            utils.OSNAME,
            utils.CPU.name, utils.CPU.architecture]) + ': '\
            + score
        bar.bar_value = float(score)/graph.max_value

    def get_formatted_result(self, result, get_zip=False):
        result = utils.get_formatted_result(result, get_zip=get_zip)
        if not result:
            make_toast('Please run benchmark first!')
            Logger.info('Benchmarkapp: Please run benchmark first! Nothing to share.')
        return result

    def run_benchmark(self, comment=None, workstation=False):
        # print('workstation: ', workstation, '<<')
        if self._benchmark_running:
            return

        self._benchmark_running = True

        self.progress = 0
        self.progress_message = 'Starting Benchmark'


        if (self._benchmark_thread and
         self._benchmark_thread.is_alive()):
            return

        from utils.bench_mark import start_benchmark
        self._benchmark_thread = start_benchmark(comment=comment, workstation=workstation)


    def stop_benchmark(self):
        # currently benchmark does not have ability to stop/pause/cancel.
        return
        self._benchmark_thread.raise_exception()

    def on_stop(self):
        self.stop_benchmark()
