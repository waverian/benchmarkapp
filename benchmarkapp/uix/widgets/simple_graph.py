'''
'''
from kivy.factory import Factory
from kivy.properties import StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder


class SimpleBarGraph(BoxLayout):
    '''                       Single Core Results
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
    size_hint_y: None
    height: dp(32)

<Bar@Label>
    bar_color: .5, .5, .5, .5
    shadow_color: .4, .4, .4, .5
    bar_value: .7
    size_hint_y: None
    height: dp(32)
    font_size: sp(13)
    text_size: self.size
    valign: 'middle'
    halign: 'right'
    canvas.before:
        Color
            rgba: root.shadow_color
        Rectangle
            size: (self.width * self.bar_value) + dp(5), self.height
            pos: self.x + dp(10), self.y - dp(5)
        Color
            rgba: root.bar_color
        Rectangle
            size: self.width*self.bar_value, self.height
            pos: self.x + dp(10), self.y

<ThisCompBar@Bar>
    text: 'This Comp: Run benchmark to get results.'
    bar_color: 0, .5, .7, 1
    shadow_color: .4, .4, .4, .5
    bar_value: .7


<Graph@ScrollView>
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
    BoxLayout
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(32)

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
            BoxLayout
                size_hint_y: None
                height: self.minimum_height
                padding: dp(10), 0, 0, 0
                ThisCompBar
                    id: this_comp_bar
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

    bar_key = StringProperty('SINGLECORE_RESULT')
    
    bar_background = StringProperty('')
    '''Background to be used for the Graph.

    `bar_background` is a ~`kivy.uix.StringProperty` defaults to `''`
    '''

    line_background = StringProperty('')
    '''Background to be used for the line on Graph.

    `line_background` is a ~`kivy.uix.StringProperty` defaults to `''`
    '''

    results = ListProperty([
        {"System": "Apple_M1_MAX", "SINGLECORE RESULT": "1036.146515", "MULTICORE RESULT": "8415.809410"},
        {"System": "rpi1-linux32", "SINGLECORE RESULT": "172.234786", "MULTICORE RESULT": "686.106247"}
        ])
    
    def on_results(self, instance, results):
        self.load_graph_from_results(results, key=self.bar_key)

    def __init__(self, *args, **kwargs):
        super(SimpleBarGraph, self).__init__(*args, **kwargs)
        self.load_graph_from_results(self.results)

    def sort_results(self, results, sort_key='SINGLECORE RESULT'):
        return sorted(results, key=lambda d: d[sort_key])

    def load_graph_from_results(self, results, key='SINGLECORE RESULT'):
        self.ids.graph.children[0].clear_widgets()
        results = self.sort_results(results, sort_key=key)
        self.max_value = max_value= int(float(results[-1][key]))
        for item in reversed(results):
            self.show_on_graph(item, max_value, key=key)

    def show_on_graph(self, item, max_value, key='SINGLECORE RESULT'):
        Bar = Factory.Bar
        Spacer = Factory.Spacer
        
        graph_content = self.ids.graph.children[0]
        bar_value = int(float(item[key]))

        bar = Bar(text=f'{item["System"]}: {bar_value}')
        bar.bar_value = bar_value/max_value
        try:
            bar.bar_color = item['bar_color']
        except KeyError:
            bar.bar_color = [0, .5, 0, 1]
        
        graph_content.add_widget(bar)


if __name__ == '__main__':
    from kivy.app import App
    class BarApp(App):
        def build(self):
            return SimpleBarGraph()
    BarApp().run()