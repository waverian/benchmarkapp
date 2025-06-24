from kivy.factory import Factory
from kivy.clock import Clock
from kivy.lang import Builder

from kivy.effects.dampedscroll import DampedScrollEffect

class MyDampedScrollEffect(Factory.DampedScrollEffect):

    def update_velocity(self, dt):
        if self.velocity == self.overscroll == 0:
            return
        super(MyDampedScrollEffect, self).update_velocity(dt)


Factory.register('MyDampedScrollEffect', module='uix.widgets.waverianscroll')



class WaverianScrollView(Factory.ScrollView):
    Builder.load_string('''
#:import utils utils
<WaverianScrollView>
    always_overscroll: False
    bar_width: dp(20)
    effect_cls: 'MyDampedScrollEffect'
    do_scroll_x: False
    # scroll_distance: dp(2)
    scroll_type: ['bars'] if utils.is_desktop else ['bars', 'content']
    smooth_scroll_end: dp(13)
    on_parent:
        if not utils.is_desktop and self.effect_y: self.effect_y.friction = .007; self.effect_y.std_dt = 1/120
        #if args[1]: self._trigger_update_from_scroll = Clock.create_trigger(self.update_from_scroll, 1/120)

        ''')

    def on_scroll_start(self, touch, check_children=True):
        if check_children:
            touch.push()
            touch.apply_transform_2d(self.to_local)
            if self.dispatch_children('on_scroll_start', touch):
                touch.pop()
                return True
            touch.pop()

        if not self.collide_point(*touch.pos):
            touch.ud[self._get_uid('svavoid')] = True
            return
        if self.disabled:
            return True
        if self._touch or (not (self.do_scroll_x or self.do_scroll_y)):
            return self.simulate_touch_down(touch)

        # handle mouse scrolling, only if the viewport size is bigger than the
        # scrollview size, and if the user allowed to do it
        vp = self._viewport
        if not vp:
            return True
        scroll_type = self.scroll_type
        ud = touch.ud
        scroll_bar = 'bars' in scroll_type


        width_scrollable = (
            (self.always_overscroll and self.do_scroll_x)
            or vp.width > self.width
        )
        height_scrollable = (
            (self.always_overscroll and self.do_scroll_y)
            or vp.height > self.height
        )

        d = {'bottom': touch.y - self.y - self.bar_margin,
             'top': self.top - touch.y - self.bar_margin,
             'left': touch.x - self.x - self.bar_margin,
             'right': self.right - touch.x - self.bar_margin}

        
        # check if touch is in bar_x(horizontal) or bar_y(vertical)
        # width_enable_overscroll or vp.width > self.width
        ud['in_bar_x'] = (scroll_bar and width_scrollable and
                          (0 <= d[self.bar_pos_x] <= self.bar_width))
        ud['in_bar_y'] = (scroll_bar and height_scrollable and
                          (0 <= d[self.bar_pos_y] <= self.bar_width))

        if 'button' in touch.profile and touch.button.startswith('scroll'):
            btn = touch.button
            m = self.scroll_wheel_distance
            e = None

            if (
                (btn == 'scrolldown' and self.scroll_y >= 1)
                or (btn == 'scrollup' and self.scroll_y <= 0)
                or (btn == 'scrollleft' and self.scroll_x >= 1)
                or (btn == 'scrollright' and self.scroll_x <= 0)
            ):
                return False

            if (
                self.effect_x
                and self.do_scroll_y
                and height_scrollable
                and btn in ('scrolldown', 'scrollup')
            ):
                e = self.effect_x if ud['in_bar_x'] else self.effect_y

            elif (
                self.effect_y
                and self.do_scroll_x
                and width_scrollable
                and btn in ('scrollleft', 'scrollright')
            ):
                e = self.effect_y if ud['in_bar_y'] else self.effect_x

            if e:
                # make sure the effect's value is synced to scroll value
                self._update_effect_bounds()
                if btn in ('scrolldown', 'scrollleft'):
                    if self.smooth_scroll_end:
                        e.velocity -= m * self.smooth_scroll_end
                    else:
                        if self.always_overscroll:
                            e.value = e.value - m
                        else:
                            e.value = max(e.value - m, e.max)
                        e.velocity = 0
                elif btn in ('scrollup', 'scrollright'):
                    if self.smooth_scroll_end:
                        e.velocity += m * self.smooth_scroll_end
                    else:
                        if self.always_overscroll:
                            e.value = e.value + m
                        else:
                            e.value = min(e.value + m, e.min)
                        e.velocity = 0
                touch.ud[self._get_uid('svavoid')] = True
                e.trigger_velocity_update()
            return True

        in_bar = ud['in_bar_x'] or ud['in_bar_y']
        if scroll_type == ['bars'] and not in_bar:
            return self.simulate_touch_down(touch)

        if in_bar:
            e =  None
            if (ud['in_bar_y'] and not
                    self._touch_in_handle(
                        self._handle_y_pos, self._handle_y_size, touch)):
                self.scroll_y = (touch.y - self.y) / self.height
            elif (ud['in_bar_x'] and not
                    self._touch_in_handle(
                        self._handle_x_pos, self._handle_x_size, touch)):
                self.scroll_x = (touch.x - self.x) / self.width

            # print(in_bar, ud['in_bar_y'], self.effect_y.velocity, self.effect_y)
            e = self.effect_y if ud['in_bar_y'] else self.effect_x
            # print('Hello', e, e.velocity, e.overscroll)
            if e:
                velocity = e.velocity
                self._update_effect_bounds()
                e.overscroll = 0
                e.velocity = 0
                e.trigger_velocity_update()

        # no mouse scrolling, so the user is going to drag the scrollview with
        # this touch.
        self._touch = touch
        uid = self._get_uid()

        ud[uid] = {
            'mode': 'unknown',
            'dx': 0,
            'dy': 0,
            'user_stopped': in_bar,
            'frames': Clock.frames,
            'time': touch.time_start,
        }

        if (self.do_scroll_x and self.effect_x and not ud['in_bar_x']
                and not ud['in_bar_y']):
            # make sure the effect's value is synced to scroll value
            self._update_effect_bounds()

            self._effect_x_start_width = self.width
            self.effect_x.start(touch.x)
            self._scroll_x_mouse = self.scroll_x

        if (self.do_scroll_y and self.effect_y and not ud['in_bar_x']
                and not ud['in_bar_y']):
            # make sure the effect's value is synced to scroll value
            self._update_effect_bounds()

            self._effect_y_start_height = self.height
            self.effect_y.start(touch.y)
            self._scroll_y_mouse = self.scroll_y

        if not in_bar:
            Clock.schedule_once(self._change_touch_mode,
                                self.scroll_timeout / 1000.)
        return True
