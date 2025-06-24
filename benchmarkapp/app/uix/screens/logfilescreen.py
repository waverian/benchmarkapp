'''Crash Reporter Module
module: apps/crashreporter.py

The Error Reporting screen/app should offer following functionality::

- Show up automatically on next launch after a crash.
- Show Last crash log.
- Offer to report the last crashlog + last `x` crash logs to developers.
- Have a default `Send to Waverian Button` & a `Share`/`Copy` to clipboard button.
- Allow user to send more information about what they were doing when the crash happened.
- Offer Option to auto report from here on so next time reports can be auto send
- Offer to try and launch mainapp and continue or exit after reporting the crash.

TODO::

- PROVIDE SYS INFO
'''
import os
from time import strftime

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.config import Config
from kivy.utils import platform
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from utils import make_toast
from natsort import natsorted

import utils

from uix.widgets import behaviors


class LogFileScreen(Screen):
    '''Look at module Documentation for details.
    '''

    Builder.load_string('''
#:import platform kivy.utils.platform
#:import make_toast utils.make_toast
#:import utils utils
#:import Window kivy.core.window.Window

<StencilButtTxt@FocusLookBehavior+ButtonBehavior+BoxLayout>
    text: ''
    source: ''
    padding: dp(9), 0, 0, 0
    Image
        allow_stretch: True
        size_hint_x: None
        width: self.height/1.2
        source: root.source
    Label:
        id: lbl
        text: root.text
        size_hint_x: None
        width: self.texture_size[0]
        font_size: dp(15)

<HLabel@Label>
    markup: True
    size_hint: 1, None
    text_size: self.width, None
    height: self.texture_size[1]


<LargeText@WaverianScrollView>
    text: ''
    font_size: sp(13)
    font_name: 'RobotoMono-Regular'
    on_text:
        lines = args[1].split('\\n')
        container.clear_widgets()
        from kivy.uix.label import Label
        from kivy.factory import Factory
        for line in lines:\
            lbl = Factory.HLabel(text=line);\
            lbl.font_size=root.font_size;\
            lbl.font_name=root.font_name;\
            container.add_widget(lbl)
    VBoxLayout
        id: container
        padding: dp(9), dp(9)
        spacing: dp(5)

<LogFileScreen@Screen>
    on_pre_enter:
        log_1.focused = True
        self.on_error_report_selected(0)
    BoxLayout
        orientation: 'vertical'
        padding: 0, dp(0), 0, 0
        # Widget
        #     size_hint_y: None
        #     height: dp(12)
        BoxLayout:
            size_hint_y: None
            height: dp(50)
            # spacing: dp(9)
            # padding: dp(-9)
            ImgButtHoverFocus:
                size_hint_x: None
                width: dp(50)
                source: 'data/theme/blue/images/left_arrow.png'
                on_release: Clock.schedule_once(lambda dt: load_screen('MainScreen'), .25)
            Label
                text: 'Crash Reporter'
        BoxLayout
            orientation: 'vertical'
            padding: dp(9), dp(9)
            spacing: dp(9)
            BoxLayout
                size_hint_y: None
                height: dp(45)
                padding: dp(-9), 0, dp(9), 0
                spacing: dp(9)
                StencilButtTxt
                    id: log_1
                    text: '#1'
                    source: 'data/theme/' + app.theme + '/images/logs.png'
                    on_release: root.on_error_report_selected(0)
                StencilButtTxt
                    text: '#2'
                    source: 'data/theme/' + app.theme + '/images/logs.png'
                    on_release: root.on_error_report_selected(1)
                StencilButtTxt
                    text: '#3'
                    source: 'data/theme/' + app.theme + '/images/logs.png'
                    on_release: root.on_error_report_selected(2)
                StencilButtTxt
                    text: '#4'
                    source: 'data/theme/' + app.theme + '/images/logs.png'
                    on_release: root.on_error_report_selected(3)
                StencilButtTxt
                    id: but_copy
                    source: 'data/theme/' + app.theme + '/images/copy.png'
                    on_release:
                        from kivy.core.clipboard import Clipboard
                        line = '\\r\\n' + ('=' * 99) + '\\r\\n'
                        body = \
                            line +\
                            (' ' * 55) + 'ERROR LOGS' +\
                            line +\
                            error_label.text.replace('\\n', '\\r\\n') +\
                            line +\
                            (' ' * 55) + 'SYS INFO' +\
                            line
                        Clipboard.copy(body)
                        make_toast('Copied')
                StencilButtTxt
                    # pos_hint: {'center_x': .5, 'center_y': .5}
                    source: 'data/theme/' + app.theme + '/images/save.png' if utils.is_desktop \
                       else 'data/theme/' + app.theme + '/images/share.png'
                    on_release: root.on_save_error_button() if utils.is_desktop  else root.on_share()
            FloatLayout
                id: fl
                WTextInput
                    id: error_label
                    font_name: 'RobotoMono-Regular'
                    font_size: dp(12)
                    text: ''
                    size: fl.size
                    pos: fl.pos
                    readonly: True
                    use_bubble: False
                    use_handles: False
                    allow_copy: False
                    on_text:
                        self.scroll_y = 0
                    scroll_from_swipe: True
                WaverianScrollView
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
            FloatLayout
                id: search_container
                size_hint_y: None
                height: dp(45)
                BoxLayout
                    id: bl_search
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        Rectangle:
                            source: 'data/theme/' + app.theme + '/images/but_cylinder.png'
                            size: self.size
                            pos: self.pos
                        Rectangle:
                            source: 'data/theme/' + app.theme + '/images/but_cylinder.png'
                            size: self.size
                            pos: self.pos
                    size: search_container.size
                    pos: search_container.pos
                    ImgButt
                        source: 'data/theme/' + app.theme + '/images/find.png'
                    WTextInput
                        id: input_search
                        multiline: False
                        hint_text: ('Enter search text here')
                        text_validate_unfocus: False
                        on_text_validate: root.on_search_next()
                    StencilButtTxt
                        size_hint_x: None
                        width: dp(63)
                        source: 'data/theme/' + app.theme + '/images/find_previous.png'
                        on_release: root.on_search_prev()
                    StencilButtTxt
                        size_hint_x: None
                        width: dp(63)
                        source: 'data/theme/' + app.theme + '/images/find_next.png'
                        on_release: root.on_search_next()
        Widget
            size_hint_y: None
            height: dp(9)
        # Widget
        #     size_hint_y: None
        #     height: app.root.ids.bottom_bar.height if not app.horiz_mode and (not app.desktop_mode or app.navigation_manager == root.manager) else 0

''')

    def __init__(self, *args, **kwargs):
        super(LogFileScreen, self).__init__(*args, **kwargs)
        self.selected_report = None
        self.current_search_line = 0
        Window.bind(keyboard_height=self.show_search_box)
    
    def show_search_box(self, instance, value):
        if utils.is_desktop:
            return
        self.ids.bl_search.y = value if value > dp(5) else self.ids.search_container.y


    @staticmethod
    def get_logs_report():
        log_dir = os.path.join(kivy.kivy_home_dir, Config.get('kivy', 'log_dir'))
        logs = [os.path.join(log_dir, log) for log in os.listdir(log_dir)]
        return natsorted(logs, reverse=True)

    def on_error_report_selected(self, number):
        try:
            self.selected_report = self.get_logs_report()[number]
        except IndexError:
            msg = f"Selected report ID {number} does not yet exists, they will show up after multiple runs of the app."
            self.ids.error_label.text = msg
            Logger.warning(msg)
            return

        if not os.path.exists(self.selected_report):
            Logger.warning(f'WaverianApp: Log you are attempting to read does not exist {self.selected_report}')
            return
        with open(self.selected_report, 'rb') as file:
            err_data = file.read()

        self.ids.error_label.text = err_data.decode('utf-8')

    def on_save_error_button(self):
        from plyer import filechooser
        from datetime import datetime

        timestamp = datetime.now().strftime("log-%y-%m-%d-%H-%M.txt")
        default_path = os.path.join(os.path.expanduser("~"), timestamp)

        filechooser.save_file(
            on_selection=self.on_save_file_selected,
            path=default_path,
            filters=[["Text file (*.txt)", "*.txt"]])

    def on_save_file_selected(self, selection):
        try:
            filename = selection[0]
        except (IndexError, TypeError):
            return

        from shutil import copyfile
        copyfile(self.selected_report, filename)

    def on_share(self):
        from utils import do_share
        data = self.ids.error_label.text # .encode('utf-8')
        app = App.get_running_app()
        path = f'{app.user_data_dir}/CrashLog.txt'
        with open(path, 'w') as fp:
            fp.write(data)

        do_share(path, 'CrashLog', filename='CrashLog.txt')

    def on_search_next(self):
        search_pattern = self.ids.input_search.text
        text_box = self.ids.error_label

        for num, line in enumerate(self.ids.error_label.text.split("\n")[self.current_search_line + 1:], self.current_search_line + 1):
            line_hit = line.lower().find(search_pattern.lower())
            if line_hit != -1:
                text_box.cursor = [0, num]
                start = sum([len(a) + 1 for a in text_box.text.split("\n")[:num]]) + line_hit
                text_box.select_text(start, start+len(search_pattern))
                self.current_search_line = num
                return

        self.current_search_line = 0
        make_toast("No more occurrences found. Starting search from the begin")


    def on_search_prev(self):
        search_pattern = self.ids.input_search.text
        text_box = self.ids.error_label

        for num, line in reversed(list(enumerate(
            text_box.text.split("\n")[:self.current_search_line], 0))):
            line_hit = line.lower().find(search_pattern.lower())
            if line_hit != -1:
                text_box.cursor = [0, num]
                start = sum([len(a) + 1 for a in text_box.text.split("\n")[:num]]) + line_hit
                text_box.select_text(start, start + len(search_pattern))
                self.current_search_line = num
                return

        self.current_search_line = len(text_box.text.split("\n"))
        make_toast("No more occurrences found. Starting search from the end")
