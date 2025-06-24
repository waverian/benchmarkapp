'''ScreenGraphDetails
'''

from kivy.uix.screenmanager import Screen
from kivy.properties import DictProperty
from kivy.clock import Clock

from kivy.lang import Builder


class ScreenGraphDetails(Screen):
    '''
    '''
    _item = DictProperty({})

    Builder.load_string('''
#:import go_back_in_history utils.go_back_in_history

<ScreenGraphDetails>
    name: 'ScreenGraphDetails'
    Magnet
        duration: 0.1
        BoxLayout:
            padding: dp(10)
            orientation: 'vertical'
            BoxLayout:
                size_hint_y: None
                height: dp(50)
                spacing: dp(9)
                padding: dp(9)
                ImgButtHoverFocus:
                    size_hint_x: None
                    width: dp(50)
                    source: 'data/theme/blue/images/left_arrow.png'
                    on_release: go_back_in_history()
                Title
                    text: 'Graph Details'
                CopySave
                    result: root._item
            WaverianScrollView:
                id: sv
                BenchResults
                    id: bench_results
                    historical: True
                    result: root._item
''')

    def on_pre_enter(self, *args):
        self.ids.sv.scroll_y = 1

    def load_graph_details(self, item):
        # from pudb import set_trace; set_trace()
        self._item = item
