'''
Mainscreen
'''

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder


class MainScreen(Screen):
    '''
    '''
    Builder.load_string('''
#:import Magnet uix.widgets.magnet.Magnet
<MainScreen>
    name: 'MainScreen'
    on_enter:
        import utils
        utils.show_status_bar()
        Clock.schedule_once(lambda dt: tcarousel.on_current_tab(tcarousel, tcarousel.current_tab), .25)
    TabbedScreen
        id: tcarousel
        tab_height: dp(63)
        Screen
            id: benchmark_screen
            name: 'Benchmark'
            on_parent: if args[1]: app.load_benchmark_info(self); Clock.schedule_once(lambda dt: tcarousel.on_current_tab(self, self.tab()), 1)
            on_enter: app.load_benchmark_info(self)
        Screen
            id: charts_single
            name: 'Single-Core\\nCharts'
            on_enter: app.load_charts(self, 'single')
        Screen
            id: charts_multi
            name: 'Multi-Core\\nCharts'
            on_enter: app.load_charts(self, 'multi')
        Screen
            id: charts_museum
            name: 'Museum'
            on_enter: app.load_museum(magnet)
            Magnet:
                id: magnet
                duration: .25
        Screen
            id: about_screen
            name: 'About'
            on_enter: app.load_about(self)
''')
