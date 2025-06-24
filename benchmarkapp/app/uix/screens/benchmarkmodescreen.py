'''BenchmarkModeScreen

    This screen displays the details about what different
benchmark modes are available and what they do.


'''

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder


class BenchmarkModeScreen(Screen):
    '''
Workstation mode
----------------
    
    A CPU throttling and a CPU cooling test, based on Multi-core workload, which tests long-term endurance. (between 10 and 30-minutes)
    This mode is only available in the Pro version of the app enabled through checkmark `Workstation` on the main benchmark page.

    .. image :: data/workstation_mode.png

Quad-core mode
--------------

    Workload for lightly-threaded applications.
    This is the default mode of the benchmark.

    .. image :: data/quadcore_mode.png
    
    '''

    Builder.load_string('''
<BenchmarkModeScreen>:
    name: "BenchmarkModeScreen"
    on_pre_enter:
        back_button.focused = True
    BoxLayout
        orientation: 'vertical'
        padding: dp(9)
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            ImgButtHoverFocus:
                id: back_button
                size_hint_x: None
                width: dp(50)
                source: 'data/theme/blue/images/left_arrow.png'
                on_release: Clock.schedule_once(lambda dt: load_screen('MainScreen'), .25)
            Label
                text: 'Benchmark Modes'
        Separator
        RstDocument:
            text_size: self.size
            colors: {'background': '#303030', 'foreground': '#ffffff', 'paragraph':  '#ffffff'}
            valign: 'top'
            halign: 'left'
            markup: True
            text: root.__self__.__doc__#.format(topic_size='27sp')
        Separator
''')
