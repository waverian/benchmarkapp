'''
Custom Behaviors are defined in this module.
'''

from kivy.app import App
from kivy.animation import Animation
from kivy.lang import Builder

from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window

is_desktop = Config.get('kivy', 'desktop') == '1'

from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.graphics import Rectangle, BorderImage, Color
from kivy.metrics import dp
from kivy.properties import (NumericProperty, StringProperty,
                             ListProperty, BooleanProperty)
from kivy.graphics import (Rectangle, Color, Ellipse, StencilPop,
                           StencilPush, StencilUnUse, StencilUse)

from kivy.uix.behaviors import CoverBehavior
from kivy.uix.image import Image
from kivy.uix.behaviors import FocusBehavior


class CoverImage(CoverBehavior, Image):

    def __init__(self, **kwargs):
        super(CoverImage, self).__init__(**kwargs)

    def on_texture(self, *args, **kwargs):
        texture = self._coreimage.texture
        self.reference_size = texture.size
        self.texture = texture


class TouchRippleBehavior(EventDispatcher):

    __events__ = ('on_released',)

    ripple_rad = NumericProperty(10)
    ripple_pos = ListProperty([0, 0])
    #141 ,188, 234
    ripple_color = ListProperty((141./256., 188./256., 234./256., 1))
    ripple_duration_in = NumericProperty(.3)
    ripple_duration_out = NumericProperty(.3)
    fade_to_alpha = NumericProperty(.3)
    ripple_scale = NumericProperty(2.0)
    ripple_func_in = StringProperty('out_quad')
    ripple_func_out = StringProperty('in_quad')

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            # self.anim_complete(self, self)
            self.ripple_pos = ripple_pos = (touch.x, touch.y)
            Animation.cancel_all(self, 'ripple_rad', 'ripple_color')
            rc = self.ripple_color
            ripple_rad = self.ripple_rad
            self.ripple_color = [rc[0], rc[1], rc[2], 1.]
            anim = Animation(
                ripple_rad=max(self.width, self.height) * self.ripple_scale,
                t=self.ripple_func_in,
                ripple_color=[rc[0], rc[1], rc[2], self.fade_to_alpha],
                duration=self.ripple_duration_in)
            anim.bind(on_complete=self.anim_complete)
            anim.start(self)
            with self.canvas:
                StencilPush()
                Rectangle(size=self.size, pos=self.pos)
                StencilUse()
                self.col_instruction = Color(
                    rgba=self.ripple_color, group='one')
                self.ellipse = Ellipse(
                    size=(ripple_rad, ripple_rad),
                    pos=(ripple_pos[0] - ripple_rad/2.,
                         ripple_pos[1] - ripple_rad/2.),
                    group='one')
                StencilUnUse()
                Rectangle(size=self.size, pos=self.pos)
                StencilPop()
            self.bind(
                ripple_color=self.set_color, ripple_pos=self.set_ellipse,
                ripple_rad=self.set_ellipse)
        return super(TouchRippleBehavior, self).on_touch_down(touch)

    def set_ellipse(self, instance, value):
        ellipse = self.ellipse
        ripple_pos = self.ripple_pos
        ripple_rad = self.ripple_rad
        ellipse.size = (ripple_rad, ripple_rad)
        ellipse.pos = (
            ripple_pos[0] - ripple_rad/2.,
            ripple_pos[1] - ripple_rad/2.)

    def set_color(self, instance, value):
        self.col_instruction.rgba = value

    def on_release(self):
        rc = self.ripple_color
        anim = Animation(
            ripple_color=[rc[0], rc[1], rc[2], 0.],
            t=self.ripple_func_out, duration=self.ripple_duration_out)
        anim.bind(on_complete=self.anim_completed)
        anim.start(self)

    def anim_complete(self, anim, instance):
        self.ripple_rad = 10
        self.canvas.remove_group('one')

    def on_released(self):
        pass

    def anim_completed(self, anim, instance):
        self.anim_complete(anim, instance)
        self.dispatch('on_released')


class HoverBehavior(object):

    hover = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super(HoverBehavior, self).__init__(*args, **kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, discard, pos):
        if not self.get_root_window():
            return
        self.hover = self.collide_point(*self.to_widget(*pos))

    def on_touch_up(self, touch):
        super(HoverBehavior, self).on_touch_up(touch)



class HoverLookBehavior(HoverBehavior):

    _animating = False

    Builder.load_string('''
#:import Clock kivy.clock.Clock
<HoverLookBehavior>
    hovering_opacity: 0
    dx: -1000
    on_hover:
        if args[1]:\
            self.hovering_opacity = .5;\
            dx=0;\
            Clock.schedule_once(self._anim_flash, .5)
        if not args[1]:\
            self.hovering_opacity = 0;\
            self.dx = -self.height;\
            self._animating = False;\
            Animation.cancel_all(self);\
            Clock.unschedule(self._anim_flash)
    canvas.after:
        Color:
            rgba: 1, 1, 1, self.hovering_opacity
        # Rectangle:
        #     source: 'data/theme/' + app.theme + '/images/waverian_glow.png'
        #     size: self.width - dp(18), self.height
        #     pos: self.x + dp(9), self.y
        Rectangle
            source: 'data/theme/' + app.theme + '/images/flash_white.png'
            size: root.height, root.height
            pos: root.dx, root.y
''')

    def _anim_flash(self, dt):
        if self._animating:
            return
        self._animating = True
        Animation.cancel_all(self)
        anim = Animation(dx=self.width+self.height, d=.45)

        def _on_complete(self, widget):
            self._animating = False

        anim.bind(on_complete=_on_complete)
        anim.start(self)


class FocusTrigger(FocusBehavior):
    '''This defines a class that triggers the focusable item when a space/enter
    key is pressed. This class can only be used with classes like
    Button/ButtonBehavior that have a `trigger_action`.
    '''

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        '''Trigger action when `space` or `enter` is pressed.
        '''
        if keycode[1] in ('enter', 'spacebar') and not modifiers:
            self.trigger_action()
            return True
        return super(FocusTrigger, self).keyboard_on_key_down(
            window, keycode, text, modifiers)


class FocusLook(object):
    Builder.load_string('''
<FocusLook>
    focus_look_width: 0
    focus_opacity: 0
    on_focused:
        from kivy.animation import Animation
        anim = Animation(\
            focus_look_width=self.width if args[1] else 0,\
            focus_opacity=.4 if args[1] else 0, d=.25)
        anim.start(self)
    canvas.after:
        Color:
            rgba: 1, 1, 1, 1 if self.focus_look_width > 10 else 0
        BorderImage
            border: 0, 0, 36, 0
            source: 'data/theme/' + app.theme + '/images/focused_overlay.png'
            pos: self.pos
            size: root.focus_look_width, dp(1)
        Color:
            rgba: 1, 1, 1, root.focus_opacity
        Rectangle
            source: 'data/theme/' + app.theme + '/images/waverian_glow.png'
            size: self.size
            pos: self.pos
''')


class FocusLookBehavior(FocusLook, FocusTrigger):

    pass


class FocusArrowKeys(FocusBehavior):
    '''This defines a class that allows the focusable item to react when a arrow up/down
    key is pressed. This class can be used with widgets that have a
    `value` property.
    '''

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        '''Trigger action when `space` or `enter` is pressed.
        '''
        # print(keycode, text, modifiers)
        if keycode[1] in ('up', 'down', 'left', 'right'):
            value = (self.step or 1) * (-1 if keycode[1] in ('down', 'left') else 1)

            if hasattr(self, 'touched'):
                Clock.unschedule(self._untouch)
                self.touched = True

            self.value = max(self.min, min(self.max, (self.value+value)))

            if hasattr(self, 'touched'):
                Clock.schedule_once(self._untouch, .25)

            return True
        return super(FocusArrowKeys, self).keyboard_on_key_down(
            window, keycode, text, modifiers)

    def _untouch(self, dt):
        self.touched = False


class FocusArrowBehavior(FocusLook, FocusArrowKeys):
    pass


class FocusSwitch(FocusBehavior, Factory.Switch):

    def on_focused(self, instance, value):
        anim = Animation(\
            focus_look_width=self.width if value else 0,\
            focus_opacity=.4 if value else 0, d=.25)
        anim.start(self)


    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        '''Trigger action when `space` or `enter` is pressed.
        '''
        # print(keycode, text, modifiers)
        if keycode[1] in ('enter', 'spacebar'):
            self.active = not self.active
            return True

        return super(FocusSwitch, self).keyboard_on_key_down(
            window, keycode, text, modifiers)


class FocusSpinner(FocusLook, FocusBehavior, Factory.Spinner):

    def on_text(self, instance, value):
        if not self.disabled or not self.parent:
            self.focus = is_desktop

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        '''Trigger action when `space` or `enter` is pressed.
        '''
        # print(keycode, text, modifiers)
        if keycode[1] in ('enter', 'spacebar'):
            self.trigger_action()
            self._dropdown.children[0].children[-1].focus = is_desktop
            return True

        return super(FocusSpinner, self).keyboard_on_key_down(
            window, keycode, text, modifiers)


class FocusSpinnerOption(FocusLook, FocusBehavior):

    def on_focused(self, instance, focus):
        scroll = self.parent.parent
        scroll.scroll_to(instance, padding=instance.height)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        '''Trigger action when `space` or `enter` is pressed.
        '''
        # print(keycode, text, modifiers)
        if keycode[1] in ('enter', 'spacebar'):
        #     if not self.parent.parent.attach_to:
        #         return
            self.trigger_action()
            return True

        if keycode[1] in ('up', 'down'):
            children = self.parent.children
            idx = children.index(self)
            try:
                lenc = len(children)
                children[idx + (-1 if keycode[1] == 'down' else 1)].focus = is_desktop
            except IndexError:
                children[0].focus = is_desktop
            return True


        return super(FocusSpinnerOption, self).keyboard_on_key_down(
            window, keycode, text, modifiers)

class DownActiveBehavior(object):

    def on_press(self):
        path_list = self.source.split('/')
        filename  = path_list[-1]
        path = '/'.join(path_list[:-1])
        file, ext = filename.split('.')

        if '_active' not in file  and '_down' not in file:
            filename = file + '_down.' + ext
            self.source = '/'.join((path, filename))


Factory.register('DownActiveBehavior', DownActiveBehavior)
Factory.register('FocusLook', FocusLook)
Factory.register('FocusSpinnerOption', FocusSpinnerOption)
Factory.register('FocusArrowBehavior', FocusArrowBehavior)
Factory.register('FocusArrowKeys', FocusArrowKeys)
Factory.register('FocusLookBehavior', FocusLookBehavior)
Factory.register('HoverBehavior', HoverBehavior)
Factory.register('HoverLookBehavior', HoverLookBehavior)
Factory.register('TouchRippleBehavior', TouchRippleBehavior)
