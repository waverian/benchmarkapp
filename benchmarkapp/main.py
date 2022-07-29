'''Main module for App entry of Livemore Loops Kivy UI App.
 Copyright (c) Waverian Team 2022.
 License @ https://github.com/waverian/benchmarkapp/tree/main/LICENSE
 '''

from env import setup_env

from kivy.app import App
from kivy.properties import (StringProperty, NumericProperty,
    ObjectProperty, BooleanProperty, DictProperty, OptionProperty, ListProperty)
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform
from kivy.core.window import Window
from kivy.resources import resource_add_path
from kivy.factory import Factory

Factory.register('TabbedCarousel', module='uix.widgets.tabbed_carousel')

from uix.benchmark_results import BenchmarkResults
from uix.widgets.simple_graph import SimpleBarGraph

import os
import utils
from utils import make_toast

resource_add_path(os.path.abspath(os.path.dirname(__file__)))

# from utils.lang import Lang

# global_lang = Lang('en')

from _version import __version__


class BenchMarkApp(App):
    '''The main purpose of this Kivy App is to create a UI with
    the following elements::
    - Benchmark results screen to display the results of benchmark.
    - Graphs comparing current results with hostorical results.
    - Display Hostorical data about the CPUs & their Architecture
    '''

    title = 'Livemore Loops'
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

    result = ObjectProperty(None)
    '''This is the result updated by the benchmark c lib to be displayed on UI.

    `result` is a ~kivy.properties.`DictProperty` defaults to `{}`
    '''

    results = ObjectProperty({})
    '''These are the individual kernel results from `result` property.

    `results` is a ~kivy.properties.`DictProperty` defaults to `{}`
    '''

    theme = StringProperty('blue')
    '''Theme for UI,  default theme is dark background with blue highlight.

    `results` is a ~kivy.properties.`DictProperty` defaults to `blue`
     '''

    rotation = OptionProperty(0, options=(0, 90, 180, 270, 360))
    '''Window Rotation usefull for some ios UI changes according
    to rotation and Status Bar appearance.

    `roation` is a ~kivy.properties.`OptionProperty` defaults to `0`
    '''

    window_width = NumericProperty('270sp')
    '''This property is updated at most once per second while window width is changing,
    used to make a delayed UI reaction to the change allowing less property dispatches.

    TODO: replace Window.width with this where possible.
     '''


    def on_start(self):
        import os
        self._benchmark_running = False
        self._benchmark_thread = None
        # initialize Benchmark screen
        self._museum = None
        self._about = None

        # bind to the keyboard to listen to
        # specific key codes
        from utils.keyboard import hook_keyboard
        Clock.schedule_once(lambda dt: hook_keyboard())
        self.window_width_trigger = Clock.create_trigger(self._update_width, 1)
        Window.bind(width=self.on_window_width)

    def on_window_width(self, instance, value):
        self.window_width_trigger()

    def _update_width(self, dt):
        self.window_width = Window.width

    def on_resume(self):
        self.stop_benchmark()
        return True

    def load_about(self, screen, reset=False):
        if not reset and self._about:
            return
        
        from uix.aboutscreen import AboutScreen
        self._about = about = AboutScreen()
        screen.add_widget(about)


    def load_benchmark_info(self, screen, reset=False):
        if not reset and self.results:
            return

        if not hasattr(self, 'benchmark_results'):
            self.benchmark_results = BenchmarkResults()
            screen.add_widget(self.benchmark_results)


        from utils import bench_mark
        bench_mark.get_results()

    def load_museum(self, screen, reset=False):
        if not reset and self._museum:
            return

        if not self._museum:
            from uix.museum import Museum
            self._museum = Museum()
            screen.add_widget(self._museum)

        utils.read_museum_data()


    def load_charts(self, screen, single_multi, force=False):
        screen = self.root.ids['charts_single' if single_multi.lower() == 'single' else 'charts_multi']

        if not  hasattr(screen, 'graph') or force:
            screen.clear_widgets()
            screen.graph = graph = SimpleBarGraph()
            screen.add_widget(graph)

            graph.bar_key = 'SINGLECORE RESULT' if single_multi.lower() == 'single' else ('MULTICORE RESULT')
            graph.title = graph.bar_key
            graph.x_axis_title = ''
            graph.y_axis_title = ''
            graph.results = utils.read_historical_data()
        else:
            graph = screen.graph

        # check and update this comp results on graph
        if self.benchmark_results.ids.lbl_singlecore.text == '00000':
            return

        # benchmark has been run, update graph with results
        bar = graph.ids.this_comp_bar
        score = self.benchmark_results.ids[
                'lbl_singlecore' if single_multi == 'single' else 'lbl_multicore'].text

        bar.text = '_'.join([
            utils.OSNAME,
            utils.CPU.name, utils.CPU.architecture]) + ': '\
            + score
        bar.bar_value = float(score)/graph.max_value
        
    def on_result(self, instance, result):
        if not result:
            return

        import math
        for kernel in ('maximum', 'average', 'geometric', 'harmonic', 'minimum'):
            for i , itv in enumerate(['value', 'value1', 'value2', 'value3']):
                val = result['results'][i][kernel]
                if math.isnan(val):
                    make_toast(f'NaN @ {kernel}: {i}', timeout=10)
                    Logger.debug(f'Benchmarkapp: NaN @ {kernel} : {i}')
                setattr(self.benchmark_results.ids[f'result_{kernel}'], itv, f'{val:.0f}')

        self.results = results = result['results']
        from utils import add_device_details_to_result
        add_device_details_to_result(result)

        if not hasattr(self, 'benchmark_results'):
            return

        content = self.benchmark_results.ids.kernel_results
        content.clear_widgets()
        c_add = content.add_widget
        kernel_keys = {
            '1': 'Hydro fragment',
            '2': 'ICCG excerpt',
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
            '14': '1-D PIC (Particle In Cell)t',
            '15': 'Casual Fortran. Development version',
            '16': 'Monte Carlo search loop',
            '17': 'Implicit, conditional computation',
            '18': '2-D explicit hydrodynamics fragment',
            '19': 'General linear recurrence equations',
            '20': 'Discrete ordinates transport conditional recurrence',
            '21': 'Matrix*matrix product',
            '22': 'Planckian distribution',
            '23': '2-D implicit hydrodynamics fragment',
            '24': 'Find location of first minimum in array'}

        for x in range(24):
            item = Factory.ResultItem()
            item.loop_hash = str(x+1)
            item.text = kernel_keys[str(x+1)]

            for i, itv in enumerate(['value', 'value1', 'value2', 'value3']):
                val = results[i]["kernel_results"][x]
                if math.isnan(val):
                    make_toast(f'NaN @ {item.loop_hash} : {item.text}: {i}', timeout=10)
                    Logger.debug(f'Benchmarkapp: NaN @ {item.loop_hash} : {item.text}: {i}')
                setattr(item, itv, f'{val:.0f}')
            c_add(item)


    def get_formatted_result(self):
        result = utils.get_formatted_result(self.result)
        if self.result['singlecore_results'] == 0.0:
            make_toast('Please run benchmark first!\nCopying empty data.')
            Logger.info('Benchmarkapp: Please run benchmark first! Nothing to share.')
        return result

    def run_benchmark(self):
        if self._benchmark_running:
            return

        self._benchmark_running = True

        self.progress = 0
        self.progress_message = 'Starting Benchmark'


        if (self._benchmark_thread and
         self._benchmark_thread.is_alive()):
            return

        from utils.bench_mark import start_benchmark
        self._benchmark_thread = start_benchmark()


    def stop_benchmark(self):
        # currently benchmark does not have ability to stop/pause/cancel.
        return
        self._benchmark_thread.raise_exception()

    def on_stop(self):
        self.stop_benchmark()


if __name__ == '__main__':
    import sys
    Logger.debug(f'Benchmark Main: {sys.argv}')

    if hasattr(sys, '_MEIPASS'):
        import os
        from kivy.resources import resource_add_path

        resource_add_path(os.path.join(sys._MEIPASS))

    BenchMarkApp().run()
