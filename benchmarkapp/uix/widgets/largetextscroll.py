from kivy.lang import Builder
from kivy.factory import Factory

Builder.load_string('''
<LargeTextScroll@FloatLayout>
    id: fl
    text: ''
    TextInput
        id: error_label
        font_name: 'RobotoMono-Regular'
        font_size: dp(12)
        text: root.text
        size: fl.size
        pos: fl.pos
        readonly: True
        use_bubble: False
        use_handles: False
        allow_copy: False
        on_text:
            self.scroll_y = 0
        scroll_from_swipe: True
    ScrollView
        id: slider
        size_hint: None, None
        size: error_label.size
        pos: error_label.pos
        on_scroll_y:
            error_label.scroll_y = int(error_label.minimum_height - (error_label.minimum_height * args[1]))
            error_label._trigger_update_graphics()
        Widget:
            size_hint_y: None
            height: error_label.minimum_height
''')

LargeTextScroll = Factory.LargeTextScroll