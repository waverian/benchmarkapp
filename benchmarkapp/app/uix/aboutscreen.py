'''About Waverian

- Show details about this applicaton
- Show Application Version
- Show Server Version
- Allow User to copy Version

'''

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

class AboutScreen(Screen):
    '''
    '''
    Builder.load_string('''
#:import __main__ __main__
#:import webbrowser webbrowser
##:import lang __main__.global_lang


<AboutScreen>
    BoxLayout
        orientation: 'vertical'
        padding: 0, dp(9), 0, 0
        # Spacer
        RelativeLayout
            Image:
                fit_mode: 'cover'
                source: 'data/splash_background.png'
            BoxLayout
                orientation: 'vertical'
                Logo
                    fit_mode: 'contain'
                BoxLayout
                    size_hint_y: None
                    height: dp(120)
                    Widget
                    ImgButtHoverFocus:
                        fit_mode: 
                        size_hint_x: None
                        width: self.height*3/4
                        source: 'data/logo/kivy-icon-512.png'
                        on_release: webbrowser.open('https://kivy.org')
                    BoxLayout
                        size_hint: None, None
                        height: dp(54)
                        width: sp(240) + self.height
                        pos_hint: {'center_y': .5}
                        Label:
                            id: lbl_version
                            text_size: sp(240), None
                            text: f'DEVICE: {utils.DEVICE}\\nOS: {utils.OSNAME} {utils.CPU.architecture}\\n App: {__main__.__version__} \\nLFK_BENCHMARK: {app.result["system_info"]["version_info"]}'
                            size_hint: None, None
                            height: dp(45)
                            width: dp(240)
                            halign: 'center'
                            valign:  'middle'
                            pos_hint: {'center_y': .5}
                        ImgButtHoverFocus:
                            fit_mode: 'contain'
                            source: 'data/theme/' + app.theme + '/images/copy.png'
                            size_hint_x: None
                            width: self.height
                            on_release:
                                from kivy.core.clipboard import Clipboard
                                Clipboard.copy(lbl_version.text)
                                from utils import make_toast
                                make_toast('Copied Version info to Clipboard')
                    Widget
            Widget:
                size_hint_y: None
                height: dp(29)
        Spacer
            size_hint_y: None
            height: dp(9)
        Button:
            size_hint_y: None
            height: dp(27)
            markup: True
            background_normal: 'data/theme/blue/images/bkank.png'
            background_down: 'data/theme/blue/images/bkank.png'
            text: '[color=#4499ff][u]https://benchmark.waverian.com[/u][/color]'
            on_release:webbrowser.open('https://benchmark.waverian.com')
        Spacer
            size_hint_y: None
            height: dp(9)
        Button:
            id: but_kivy
            size_hint_y: None
            height: dp(27)
            markup: True
            background_normal: 'data/theme/blue/images/bkank.png'
            background_down: 'data/theme/blue/images/bkank.png'
            text: '[color=#4499ff][u]Made using Kivy Framework. [/u][/color]'
            on_release: webbrowser.open('https://kivy.org')
        Spacer
            size_hint_y: None
            height: dp(9)
        Button
            opacity: .3
            size_hint_y: None
            height: dp(45)
            text: 'Logs'
            on_release: load_screen('LogFileScreen')
        Spacer
            size_hint_y: None
            height: dp(9)
        Button
            opacity: .3
            size_hint_y: None
            height: dp(45)
            text: 'Benchmark mode details'
            on_release: load_screen('BenchmarkModeScreen')
        Spacer
            size_hint_y: None
            height: dp(9)
 ''')
