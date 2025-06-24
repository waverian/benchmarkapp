from functools import partial
import threading

from platform import architecture
from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.utils import platform

from utils import make_toast

app = App.get_running_app()


class MuseumDetails(Factory.VBoxLayout):

    popup = Builder.load_string('''
#:import Window kivy.core.window.Window
#:import is_desktop utils.is_desktop
Popup
    # size_hint: None, None
    # size: min(dp(700), Window.width), min(dp(700), Window.height)
    imgfile: ''
    title: self.imgfile
    BoxLayout
        orientation: 'vertical'
        FloatLayout
            id: fl
            ScatterLayout
                id: sc_layout
                do_rotation: not is_desktop
                Image
                    id: img
                    fit_mode: 'contain'
                    source: root.imgfile
                    on_parent:
                        if args[1]: self.size = fl.size
        Slider:
            id: scale_slider
            size_hint: 1, None
            height: dp(45)
            min: dp(0.2)
            max: dp(1)
            on_value:
                sc_layout.scale = args[1]
                # img.center = fl.to_widget(*fl.center)
        MuseumButton:
            size_hint_y: None
            height: dp(54)
            text: 'dismiss'
            on_release: root.dismiss()
    ''')

    Builder.load_string('''
<MuseumDetails>
    Spacer
        height: dp(4)
    MuseumTitle
        id: title
    Spacer
        opacity: 0
        height: dp(7)        
    
    VBoxLayout
        orientation: 'vertical' if root.width < dp(920) else 'horizontal'
        VBoxLayout
            BoxLayout
                id: bl_image
                size_hint_y: None
                height: dp(159)  if root.width < dp(920) else bl_content.width/2
                padding: dp(10)
                MuseumImage
                    id: image
                    fit_mode: 'contain'
                    # size_hint_x: None
                    # width: self.texture_size[0]/self.texture_size[1] * bl_image.height
                    on_release:
                        popup = root.popup
                        popup.imgfile = self.imgfile
                        popup.title = title.text
                        popup.ids.sc_layout.rotation = 0
                        popup.ids.sc_layout.scale = 1
                        popup.ids.scale_slider.value = 1
                        popup.ids.sc_layout.pos = 0, 0
                        popup.open()

                # MuseumImage:
                #     id: image2
                #     source: 'benchmarkapp/data/theme/blue/images/dummy_cpu_logo.png'
                #     fit_mode: 'contain'
                #     size_hint_x: None
                #     width: self.texture_size[0]/self.texture_size[1] * bl_image.height
        VBoxLayout
            id: bl_content
            Spacer
                height: dp(12)
            MuseumTitle:
                text: 'Generation'
                bold: True
                font_name: 'Roboto-Bold'
                halign: 'left'
            Spacer
                opacity: 0
                height: dp(12)
                
            MuseumLabel
                id: generation
            Spacer
                height: dp(4)
            MuseumTitle:
                text: 'Cache'
            Spacer
                opacity: 0
                height: dp(12)
            MuseumLabel
                id: cache
                key: "Cache Info\\n"
                value: "No Data\\n\\n"
            Spacer
                height: dp(4)
            StencilView
                id: sv
                size_hint: 1, None
                height: min(historic_label.texture_size[1], dp(200))
                Label
                    id: historic_label
                    top: sv.top
                    x: sv.x
                    width: sv.width
                    text: '\\nNo Data\\n'
                    text_size: self.width, None
                    height: self.texture_size[1] + dp(45)
                MuseumToggleButton
                    background_color: .5, .5, .5, ( 1 if self.state == 'normal' else .2)
                    background_down: self.background_normal
                    text: 'Show More' if self.state == 'normal' else 'Show Less'
                    width: sv.width
                    height: dp(45)
                    x: sv.x
                    top: sv.y + (0 if sv.height < dp(200) else (self.height - dp(2) ))
                    on_state:
                        from kivy.animation import Animation
                        Animation(height = historic_label.height if args[1] == 'down' else dp(200)).start(sv)

    Spacer
        height: dp(17)
        opacity: 0
''')


    def update_data(self, data):
        threading.Thread(target=self._update_data, args=(data,)).start()
        # self._update_data(data)

    def _update_data(self, data):
        # from pudb import set_trace; set_trace()
        data = data['cpu']
        cpu_name = list(data.keys())[0]
        sids = self.ids
        cpu_details = data[cpu_name]
        sig = sids.generation
        sig.key = ''
        sig.value = ''
        sic = sids.cache
        sic.key = ''
        sic.value = ''
        sids.title.text = str(cpu_name)
        def update_image(sids):
            imgfile = cpu_details['image']
            fln = imgfile[:-4]
            if platform.startswith('win'):
                fln = fln.replace('\\', '/')
            sids.image.source = 'atlas://' + fln
            sids.image.imgfile = imgfile
        Clock.schedule_once(lambda dt: update_image(sids))
        #All in one text
        #self.ids.historic_label.text = ''.join([f'{key} : {value}\n' for key, value in cpu_details.items() if key!='image'])
        hlabel = sids.historic_label

        for key, value in cpu_details.items():
            low_key = key.lower()
            if low_key.startswith('image'):
                continue
            if low_key.startswith('historic'):
                def set_text(text):
                    hlabel.text = str(text)
                Clock.schedule_once(lambda dt: set_text(value))
            elif low_key.startswith((
                'generation', 'example', 'architecture', 'instruction',
                'cores', 'technology', 'introduced', 'die size', 'transistors', 'frequency', 'cache')):
                x = sig
                if low_key.startswith('cache'):
                    x = sic
                if key:
                    x.key += key + '\n'
                if value:
                    x.value += value + '\n'

        def show(*args):
            self.opacity = 1
        Clock.schedule_once(show, .25)

class Museum(Factory.TabbedPanelHighlight):

    initial_delay = 1

    Builder.load_string('''
#:import Window kivy.core.window.Window
<MuseumImage@ButtonBehavior+Image>
    opacity: .5 if self.state == 'down' else 1
    fit_mode: 'contain'
    # size_hint: 1, None
    # height: dp(100)

<MuseumLabel@BoxLayout>
    key: ''
    value: ''
    size_hint_y: None
    height: self.minimum_height - dp(9)
    spacing: dp(29)
    Label
        font_size: sp(13)
        size_hint: 1, None
        text: root.key
        text_size: self.width, None
        pos_hint: {'center_y': .5}
        height: self.texture_size[1]
        valign: 'middle'
    Label
        font_size: sp(13)
        pos_hint: {'center_y': .5}
        size_hint: 1, None
        text: root.value
        text_size: self.width, None
        height: self.texture_size[1]
        valign: 'middle'



<MuseumHeader@FocusLookBehavior+TabbedPanelHeader>
    color: 1, 1, 1, 0
    Image
        fit_mode: 'contain'
        height: root.height - dp(9)
        source: 'data/theme/blue/images/{}.png'.format(root.text.lower().replace(' ', '_'))
        center: root.center
    

<MuseumTitle@Label>
    size_hint_y: None
    dheight: sp(14)
    height: sp(14)
    font_size: sp(14)
    bold: True


<MuseumItem@WaverianScrollView>
    VBoxLayout:
        id: content
        padding: dp(20)

<Museum>
    do_default_tab: False
    tab_pos: 'top_mid'
    tab_width: self.width/4
''')
    tab_line = None

    def __init__(self, *args, **kwargs):
        super(Museum, self).__init__(*args, **kwargs)
        app.bind(museum_data=self.on_museum_data)

    def load_data(self, title, header):
        items = app.museum_data[title.replace(' ', '_')]
        ai = header.content
        add_widget = ai.ids.content.add_widget
        from operator import itemgetter
        if title.lower() in ['intel', 'amd']:
            sorted_keys = sorted(items, key=lambda d: float(items[d]['Introduced']))
        else:
            sorted_keys = sorted(items.keys())

        # from pudb import set_trace; set_trace()
        # ai.data = [{'cpu':{i:app.museum_data[title.replace(' ', '_')][i]}} ]
        for idx, i in enumerate(sorted_keys):
            mi = MuseumDetails()
            mi.opacity = 0
            # mi.size = self.width, dp(664)

            add_widget(mi)
            mi.update_data({'cpu':{i:items[i]}})

    def on_current_tab(self, instance, value):
        # if not value.data_loaded:
            # make_toast('Please Wait. Loading Data...')
        self._on_current_tab(instance, value)

    def _on_current_tab(self, instance, value):
        # self.animate_tab_to_center(value)
        if not value.data_loaded:
            self.load_data(value.text, value)
            value.data_loaded = True
            # make_toast(f'Data for {value.text} Successfully loaded', timeout=1)
        instance = value


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
