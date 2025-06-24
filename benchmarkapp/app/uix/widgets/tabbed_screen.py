from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.properties import ObjectProperty, ListProperty
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp
from kivy.lang import Builder
from weakref import ref

from .behaviors import FocusLookBehavior

app = App.get_running_app()

Builder.load_string('''    
                    
<TabbedPanelHeader>
    bold: True
    text_size: self.width, self.height
    font_size: min(sp(13), (self.width/6))
    background_normal: 'data/theme/' + app.theme + '/images/bkank.png'
    background_down: 'data/theme/' + app.theme + '/images/bkank.png'
    # size_hint_x: None
    # width: (self.texture_size[0] if self.texture_size and self.texture and self.text else sp(150)) + sp(20)

<ActiveGlowHeader@TabbedPanelHeader>
    active: root.state == 'down'
    # color: (1/255, 74/255, 100/255, 4) if self.active else (1, 1, 1, 1)
    canvas.before:
        Color: 
            rgba: 1, 1, 1, 1 if self.state == 'down' else 0
        Rectangle:
            source: 'data/theme/' + app.theme + '/images/waverian_glow_low.png'
            size: self.width, self.height
            pos: self.x, self.y

<FocusableHeader@FocusLookBehavior+ActiveGlowHeader>

''')
    

class TabbedPanelHighlight(Factory.TabbedPanel):
    '''Custom TabbedPanel with a highlight line
    '''
    
    ctpos = ListProperty([0, 0])
    
    ctsize = ListProperty([0, 0])

    initial_delay = 2
    
    Builder.load_string('''
<TabbedPanelStrip>
    canvas.after:
        Color:
            rgba: app.font_color_dull[:3] + [.3]
        BorderImage:
            border: 0, 0, 36, 0
            source: 'data/theme/' + app.theme + '/images/focused_overlay.png'
            pos: self.pos
            size: self.width, dp(36)
<TabbedPanelHighlight>
    canvas.after:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.ctpos
            size: self.ctsize
    on_current_tab:
        # print('current_tab', self.current_tab)
        self._update_tab_line(self.current_tab)
''')
    
    def on_parent(self, instance, value):
        if value:
            Clock.schedule_once(
                lambda dt: self._update_tab_line(
                    self.current_tab, animate=False), self.initial_delay)
    
    def on_pos(self, instance, pos):
        self._update_tab_line(self.current_tab)
    
    def on_size(self, instance, size):
        self._update_tab_line(self.current_tab)
    
    def _update_tab_line(self, tab, animate=True):
        ctpos = tab.x, self.top - tab.parent.tabbed_panel.tab_height
        ctsize = tab.width, dp(2)
        if animate:
            Animation(ctpos=ctpos, ctsize=ctsize, d=.25).start(self)
        else:
            self.ctpos = ctpos
            self.ctsize = ctsize
    

class TabbedScreen(Factory.TabbedPanelHighlight):
    '''Custom TabbedPanel using a carousel used in the Main Screen
    '''
    
    Builder.load_string('''
<TabbedScreen>
    manager: sm
    do_default_tab: False
    tab_width: self.width/5
    ScreenManager:
        id: sm
        on_pre_enter:
''')
    
    manager = ObjectProperty(None)

    def on_current_tab(self, instance, value):
        pass

    def switch_to(self, header):
        # we have to replace the functionality of the original switch_to
        if not header:
            return
        if not hasattr(header, 'screen'):
            header.content = self.manager
            super(TabbedScreen, self).switch_to(header)
            try:
                tab = self.tab_list[-1]
            except IndexError:
                return
            self._current_tab = tab
            tab.state = 'down'
            return

        self.current_tab.state = "normal"
        header.state = 'down'
        self._current_tab = header
        # set the carousel to load  the appropriate slide
        # saved in the screen attribute of the tab head
        self.manager.switch_to(header.screen)


    def add_widget(self, widget, index=0):
        if isinstance(widget, Factory.Screen):
            self.manager.add_widget(widget)
            tp = Factory.FocusableHeader()
            tp.screen = widget
            widget.tab = ref(tp)
            widget.bind(name=tp.setter('text'))
            widget = tp
        super(TabbedScreen, self).add_widget(widget, index=index)
