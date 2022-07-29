from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder

from utils import make_toast

app = App.get_running_app()

class Museum(Factory.TabbedPanel):
    Builder.load_string('''
#:import Window kivy.core.window.Window
<MuseumImage@TreeViewNode+Image>
    size_hint_y: None
    height: dp(120)
    allow_stretch: True
    source: root.source

<HistoricLabel@BoxLayout>
    orientation: 'vertical'
    key: ''
    value: ''
    size_hint_y: None
    height: self.minimum_height
    padding: dp(9)
    BoxLayout
        size_hint_y: None
        height: self.minimum_height
        Label
            id: lbl
            font_size: sp(12)
            size_hint: None, None
            size: self.texture_size
            text: root.key
    Widget
        size_hint_y: None
        height: sp(12)
    BoxLayout
        size_hint_y: None
        height: self.minimum_height
        Label
            id: lbl2
            font_size: sp(12)
            halign: 'left'
            size_hint: None, None
            text_size: app.window_width - dp(40), None
            size: self.texture_size
            text: root.value

<MuseumLabel@BoxLayout>
    key: ''
    value: ''
    size_hint_y: None
    height: self.minimum_height
    BoxLayout
        size_hint_y: None
        height: self.minimum_height
        Label
            id: lbl
            font_size: sp(12)
            size_hint: None, None
            size: self.texture_size
            text: root.key
    BoxLayout
        size_hint_y: None
        height: self.minimum_height
        Label
            id: lbl
            font_size: sp(12)
            size_hint: None, None
            size: self.texture_size
            text: root.value

<MuseumHeader@FocusableTabbedPanelHeader>

<MuseumTitle@Label>

<MuseumItem@ScrollView>
    BoxLayout:
        id: content
        padding: dp(20)
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height

<Museum>
    do_default_tab: False
    tab_pos: 'top_mid'
    tab_width: self.width/4
''')
    tab_line = None

    def __init__(self, *args, **kwargs):
        super(Museum, self).__init__(*args, **kwargs)
        app.bind(museum_data=self.on_museum_data)

    def animate_tab_to_center(self, value):
        scrlv = self._tab_strip.parent
        if not scrlv:
            return
        idx = self.tab_list.index(value)
        n = len(self.tab_list)
        if idx in [0, 1]:
            scroll_x = 1
        elif idx in [n-1, n-2]:
            scroll_x = 0
        else:
            scroll_x = 1. * (n - idx - 1) / (n - 1)
        mation = Factory.Animation(scroll_x=scroll_x, d=.25)
        mation.cancel_all(scrlv)
        mation.start(scrlv)

    def load_data(self, title, header):
        items = app.museum_data[title.replace(' ', '_')]
        ai = header.content
        add_widget = ai.ids.content.add_widget
        try:
            sorted_keys = sorted(items.keys(), key=lambda d: float(items[d]['Generation of Intel Architecture']))
        except KeyError:
            try:
                sorted_keys = sorted(items.keys(), key=lambda d: float(items[d]['Generation of AMD Architecture ']))
            except KeyError:
                sorted_keys = sorted(items.keys())

        for cpu in sorted_keys:
            cpu_node = Factory.MuseumTitle(text=cpu.upper().replace('_', ' '))
            # add_widget(Factory.Spacer())
            add_widget(cpu_node)
            add_widget(Factory.Spacer())
            cpudetail = items[cpu]
            for idx, key in enumerate(cpudetail):
                if key == 'image':
                    # child = Factory.Image(source='atlas://data/museum/Apple/Apple_A4_Chip')
                    child = Factory.MuseumImage(source='atlas://' + cpudetail[key][:-4])
                else:
                    child = (Factory.HistoricLabel() 
                        if key.lower().startswith('historic') else 
                        Factory.MuseumLabel())
                    # child.background_color = (1, 1, 1, .2 if idx%2 ==0 else 1)
                    child.key = key
                    child.value = cpudetail[key]
                if '?' not in cpudetail[key]:
                    add_widget(child)
                if key.lower() in ('tdp', 'memory size, max', 'historical note:', 'historic note:'):
                    add_widget(Factory.Spacer())

    def on_current_tab(self, instance, value):
        if not value.data_loaded:
            make_toast('Please Wait. Loading Data...')
        Clock.schedule_once(lambda dt: self._on_current_tab(instance, value), .25)

    def _on_current_tab(self, instance, value):
        self.animate_tab_to_center(value)
        if not value.data_loaded:
            self.load_data(value.text, value)
            value.data_loaded = True
            make_toast(f'Data for {value.text} Successfully loaded', timeout=1)
        instance = value
        if not self.tab_line:
            with instance.canvas.after:
                    Color(*app.font_color_dull[:3], 2, mode='rgba')
                    self.tab_line = Rectangle(
                        pos = (instance.x, instance.y),
                        size = (instance.width, dp(2)))

                    Color(*app.font_color_dull[:3], .2, mode='rgba')
                    Rectangle(pos=instance.pos, size=(self.width, dp(2)))
            return
        Animation(
            pos = instance.pos,
            size=(instance.width, dp(2)),
            duration=.5, transition='in_out_quart').start(self.tab_line)


    def on_museum_data(self, instance, value):
        first_tab = None
        for item in value:
            header = Factory.MuseumHeader(text=item.replace('_', ' '))
            ai = Factory.MuseumItem()
            header.data_loaded = False
            ai.tab = header
            header.content = ai
            if not first_tab:
                first_tab = True
                header.focused = True
            self.add_widget(header)
            # items = value[item]

