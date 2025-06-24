'''
'''
from kivy.factory import Factory
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock

from utils import load_screen


class SimpleBarGraph(BoxLayout):
    '''                       Single/Multi Core Results
                 ^
        Apple M2 |================ Non Optimised
                 |================== Optimised
                 |
        Xeon XYZ |============= Non Optimised
                 |==================== Optimised
                 |
    ThreadRipper |============== Non Optimised
                 |=======================  Optimised
                 |
                  ----------------------------------->
    '''

    Builder.load_string('''
<Title@Label>
    bold: True
    size_hint_y: None
    height: dp(32)

<XLabel@Label>
    # Label for Graph
    canvas.before:
        PushMatrix
        Rotate:
            angle: 90
            origin: self.center
    canvas.after:
        PopMatrix
    size_hint_x: None
    width: dp(32)

<YLabel@Label>
    # Label for Graph 
    size_hint_y: None
    height: dp(32)

<Bar@ButtonBehavior+Label>
    major_gen: False
    on_major_gen: self.bar_scale =  1.8 if args[1] else 1
    bar_color: .5, .5, .5, .5
    shadow_color: .4, .4, .4, .5
    bar_value: .7
    size_hint_y: None
    bar_scale: 1
    height: dp(32 * self.bar_scale)
    font_size: sp(13 * (self.bar_scale - .2))
    text_size: self.size
    valign: 'middle'
    halign: 'right'
    opacity: .5 if self.state == 'down' else 1
    canvas.before:
        Color:
            rgba: root.shadow_color
        BoxShadow
            size: ((self.width - dp(10 * self.bar_scale))*self.bar_value) + dp(2), self.height + dp(2)
            pos: self.x + dp(10), self.y - dp(2 * self.bar_scale)
            blur_radius: dp(15)
            border_radius: dp(10), dp(10), dp(10), dp(10)
            offset: dp(5 * self.bar_scale), dp(-5 * self.bar_scale)
        Rectangle
            size: ((self.width - dp(10 * self.bar_scale)) * self.bar_value), self.height
            pos: self.x + dp(20), self.y - dp(10 * self.bar_scale)
        Color
            rgba: root.bar_color
        Rectangle
            size: ((self.width - dp(10 * self.bar_scale))*self.bar_value) + dp(2), self.height + dp(2)
            pos: self.x + dp(10), self.y - dp(2)
    canvas.after:
        Color
            rgba: 1, 1, 1, 1
        Line
            # width: dp(1)
            points:
                self.x + dp(10), self.y - dp(2),\
                self.x + dp(10), self.top,\
                self.x + ((self.width - dp(10 * self.bar_scale))  * self.bar_value) + dp(12), self.top,\
                self.x + ((self.width - dp(10 * self.bar_scale)) * self.bar_value) + dp(12), self.y - dp(2)
        # Color
        #     rgba: root.shadow_color[:3] + [.5]
        # Line
        #     width: dp(1)
        #     points:
        #         self.x + ((self.width - dp(10)) * self.bar_value) + dp(12), self.y - dp(2),\
        #         self.x + dp(10), self.y - dp(2)
        Color:
            rgba: 1, 1, 1, 1
        Line:
            # width: dp(1)
            source: ''
            points:
                self.x + dp(10), self.y - dp(2),\
                self.x + dp(20), self.y - dp(10 * self.bar_scale),\
                self.x + ((self.width - dp(10)) * self.bar_value) + dp(20), self.y - dp(10 * self.bar_scale),\
                self.x + ((self.width - dp(10 * self.bar_scale)) * self.bar_value) + dp(12), self.y - dp(2),\
                self.x + ((self.width - dp(10 * self.bar_scale)) * self.bar_value) + dp(12), self.top,\
                self.x + ((self.width - dp(10)) * self.bar_value) + dp(20), self.top - dp(10 * self.bar_scale),\
                self.x + ((self.width - dp(10)) * self.bar_value) + dp(20), self.y - dp(10 * self.bar_scale)
        Color:
            rgba: root.shadow_color[:3] + [.5]
        Line:
            # width: dp(1)
            points:
                self.x + ((self.width - dp(10)) * self.bar_value) + dp(12), self.y - dp(2),\
                self.x + ((self.width - dp(10)) * self.bar_value) + dp(12), self.top



<ThisCompBar@Bar>
    text: 'This Comp: Run benchmark to get results.'
    bar_color: 0, .5, .7, 1
    shadow_color: 0, .4, .6, 1
    bar_value: .1


<Graph@WaverianScrollView>
    line_source: ''
    line_color: .5, .5, .5, 1
    canvas.after:
        Color:
            rgba: root.line_color
        Line
            width: dp(2)
            source: root.line_source
            points: self.x + dp(10), self.y, self.x + dp(10), self.top - dp(10)
        Line
            width: dp(2)
            source: root.line_source
            points: self.x + dp(10), self.y, root.right, self.y
    VBoxLayout
        id: content
        padding: dp(10)
        spacing: dp(45)

<SimpleBarGraph>
    orientation: 'vertical'
    canvas.before:
        Color:
            rgba: root.background_color
        Rectangle:
            source: root.bar_background
            size: self.size
            pos : self.pos
    Title
        color: root.title_color
        text: root.title
    BoxLayout
        XLabel
            color: root.x_axis_title_color
            text: root.x_axis_title
        BoxLayout
            orientation: 'vertical'
            spacing: dp(10)
            VBoxLayout
                padding: dp(10), 0, 0, 0
                ThisCompBar
                    id: this_comp_bar
            Button
                id: but_major_minor
                size_hint_y: None
                height: dp(45)
                on_release: cb_major_minor.active = not cb_major_minor.active
                background_normal: f'data/theme/{app.theme}/images/bkank.png'
                background_down: f'data/theme/{app.theme}/images/bkank.png'
                BoxLayout
                    size: but_major_minor.size
                    pos: but_major_minor.pos      
                    Label
                        text: 'Show all results. '
                    CheckBox   
                        id: cb_major_minor
                        size_hint_x: None
                        width: dp(32)
                        active: False
                        on_active:
                            root.results = utils.read_historical_data(show_all=args[1])
                            graph.ids.content.spacing = dp(32 if args[1] else 45)
            Graph
                id: graph
                bar_background: root.bar_background
                line_source: root.line_background
        XLabel
    YLabel
        color: root.y_axis_title_color
        text: root.y_axis_title

''')


    background_color = ListProperty([1, 1, 1, 0])
    '''Color to tint background image with.

    `Background_color` is a ~`kivy.uix.ListProperty` defaults to `[1, 1, 1, .2]`
    '''

    title = StringProperty('Title Here')
    '''Title of Bar Chart that is displayed on top mid.

    `title` is a ~`kivy.uix.StringProperty` defaults to `Title Here`
    '''

    title_color = ListProperty([.5, .5, .5, 1])

    x_axis_title = StringProperty('x_axis_title')
    '''X axis title of Bar Chart that is displayed on left mid of the bar

    `x_axis_title` is a ~`kivy.uix.StringProperty` defaults to `x_axis_title`
    '''

    x_axis_title_color = ListProperty([.5, .5, .5, 1])
    '''
    '''

    y_axis_title = StringProperty('y_axis_title')
    '''`y_axis_title` of Bar Chart that is displayed on bottom mid of the bar

    `y_axis_title` is a ~`kivy.uix.StringProperty` defaults to `y_axis_title`
    '''

    y_axis_title_color = ListProperty([.5, .5, .5, 1])
    '''
    '''

    bar_key = ObjectProperty(lambda d: d['full_result']['non_optimized']['score'])

    bar_background = StringProperty('')
    '''Background to be used for the Graph.

    `bar_background` is a ~`kivy.uix.StringProperty` defaults to `''`
    '''

    line_background = StringProperty('')
    '''Background to be used for the line on Graph.

    `line_background` is a ~`kivy.uix.StringProperty` defaults to `''`
    '''

    results = ListProperty([])

    def on_results(self, instance, results):
        self.load_graph_from_results(results)

    def __init__(self, *args, **kwargs):
        super(SimpleBarGraph, self).__init__(*args, **kwargs)
        # self.load_graph_from_results(self.results)

    def load_graph_from_results(self, results):
        self.ids.graph.children[0].clear_widgets()
        results = sorted(results, key=self.bar_key)
        # from pudb import set_trace; set_trace()
        self.max_value = max_value = int(self.bar_key(results[-1]))
        for item in reversed(results):
            self.show_on_graph(item, max_value)

    def show_on_graph(self, item, max_value):
        Bar = Factory.Bar

        graph_content = self.ids.graph.children[0]
        bar_value = int(float(self.bar_key(item)))
        cpu_name = item['system_info']['System'].replace('_', ' ')
        try:
            cp_name = item['system_info']['cpu_name'].strip()

            #not used but needed for raising error
            cp_encoded = cp_name.encode('utf-8')

            if not "No CPUID".lower() in cp_name.lower():
                cpu_name = item['system_info']['cpu_name']
            else:
                item['system_info']['cpu_name']  = cpu_name
        except UnicodeEncodeError:
            item['system_info']['cpu_name'] = cpu_name
        bar = Bar(text=f'{cpu_name}: {bar_value}')
        bar.bar_value = bar_value/max_value
        bar.bar_color = [0, .6, 0, 1]
        bar.shadow_color = [0, .4, 0, 1]
        bar.major_gen = item['major_gen']
        bar.bind(on_release=lambda *argss: self._show_graph_details(item))

        graph_content.add_widget(bar)

    def _show_graph_details(self, item):
        scr = load_screen('ScreenGraphDetails', load_only=True)
        scr.load_graph_details(item)
        scr.size = self.size
        Clock.schedule_once(lambda *args: load_screen('ScreenGraphDetails'), .5)


if __name__ == '__main__':
    from kivy.app import App
    class BarApp(App):
        def build(self):
            return SimpleBarGraph()
    BarApp().run()
