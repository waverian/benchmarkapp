from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp
from kivy.lang import Builder
from weakref import ref

from .behaviors import FocusLookBehavior

app = App.get_running_app()


class FocusableTabbedPanelHeader(FocusLookBehavior, Factory.TabbedPanelHeader):
    pass

class MCarousel(Factory.Carousel):
    def on_touch_move(self, *args, **kwargs):
        return super(Factory.Carousel, self).on_touch_move(*args, **kwargs)

class TabbedCarousel(Factory.TabbedPanel):
    '''Custom TabbedPanel using a carousel used in the Main Screen
    '''
    Builder.load_string('''
<TabbedPanelHeader>
    bold: True
    text_size: self.width, self.height/2.5
    valign: 'top'
    color: (1, 1, 1, 1) if self.state == 'down' else app.font_color_dull
    font_size: min(sp(13), (self.width/6))
    background_normal: 'data/theme/' + app.theme + '/images/bkank.png'
    background_down: 'data/theme/' + app.theme + '/images/bkank.png'
    # size_hint_x: None
    # width: (self.texture_size[0] if self.texture_size and self.texture and self.text else sp(150)) + sp(20)
    

<TabbedCarousel>
    carousel: carousel
    do_default_tab: False
    tab_width: self.width/5
    MCarousel:
        scroll_timeout: 120
        scroll_distance: '20dp'
        anim_type: 'out_quart'
        min_move: .05
        anim_move_duration: .1
        anim_cancel_duration: .72
        on_index: root.on_index(*args)
        id: carousel
''')

    carousel = ObjectProperty(None)

    tab_line = None

    def on_size(self, instance, size):
        try:
            self.tab_line.size = instance.current_tab.width, dp(2)
            self.highlight_line.size = Window.width, dp(2)
        except AttributeError:
            pass

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

    def on_current_tab(self, instance, value):
        self.animate_tab_to_center(value)
        instance = value
        if not self.tab_line:
            with instance.canvas.after:
                Color(*app.font_color_dull[:3], 2, mode='rgba')
                self.tab_line = Rectangle(
                    pos = (instance.x, instance.y),
                    size = (instance.width, dp(2)))

                Color(1, 1, 1, 1, mode='rgba')
                self.highlight_line = Rectangle(
                    source= 'data/theme/blue/images/focused_overlay.png',
                    pos=instance.pos,
                    size=(Window.width, dp(19)))
            return
        Animation(
            pos = instance.pos,
            size=(instance.width, dp(2)),
            duration=.5, transition='in_out_quart').start(self.tab_line)

    def on_index(self, instance, value):
        current_slide = instance.current_slide

        if not hasattr(current_slide, 'tab'):
            return
        tab = current_slide.tab()
        tab.text = current_slide.name
        ct = self.current_tab
        try:
            if ct.text != tab.text:
                carousel = self.carousel
                carousel.slides[ct.slide].dispatch('on_leave')
                self.switch_to(tab)
                carousel.slides[tab.slide].dispatch('on_enter')
        except AttributeError:
            current_slide.dispatch('on_enter')

    def switch_to(self, header):
        # we have to replace the functionality of the original switch_to
        if not header:
            return
        if not hasattr(header, 'slide'):
            header.content = self.carousel
            super(TabbedCarousel, self).switch_to(header)
            try:
                tab = self.tab_list[-1]
            except IndexError:
                return
            self._current_tab = tab
            tab.state = 'down'
            return

        carousel = self.carousel
        self.current_tab.state = "normal"
        header.state = 'down'
        self._current_tab = header
        # set the carousel to load  the appropriate slide
        # saved in the screen attribute of the tab head
        slide = carousel.slides[header.slide]
        if carousel.current_slide != slide:
            carousel.current_slide.dispatch('on_leave')
            carousel.load_slide(slide)
            slide.dispatch('on_enter')

    def add_widget(self, widget, index=0):
        if isinstance(widget, Factory.Screen):
            self.carousel.add_widget(widget)
            tp = FocusableTabbedPanelHeader()
            tp.slide = self.carousel.slides.index(widget)
            widget.tab = ref(tp)
            widget.bind(name=tp.setter('text'))
            widget = tp
        super(TabbedCarousel, self).add_widget(widget, index=index)