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
##:import lang __main__.global_lang

<ImgButtHoverFocus@FocusLookBehavior+ImgButt>


<AboutScreen>
    BoxLayout
        orientation: 'vertical'
        padding: 0, dp(9), 0, 0
        # Spacer
        Logo
            allow_stretch: True
        # Widget
        BoxLayout
            size_hint_y: None
            height: dp(36)
            Widget
            Label:
                id: lbl_version
                text_size: sp(240), None
                text: f'OS: {utils.OSNAME} {utils.CPU.architecture}\\n App: {__main__.__version__} \\nLFK_BENCHMARK: {app.result["version"]}'
                size_hint_x: None
                width: dp(240)
                halign: 'center'
                valign:  'middle'
            ImgButtHoverFocus:
                allow_stretch: True
                source: 'data/theme/' + app.theme + '/images/copy.png'
                size_hint_x: None
                width: self.height
                on_release:
                    from kivy.core.clipboard import Clipboard
                    Clipboard.copy(lbl_version.text)
                    from utils import make_toast
                    make_toast('Copied Version info to Clipboard')
            Widget
        # Widget
        #     size_hint_y: None
        #     height: dp(54)
        Button:
            size_hint_y: None
            height: dp(54)
            markup: True
            background_normal: 'data/theme/blue/images/bkank.png'
            background_down: 'data/theme/blue/images/bkank.png'
            text: '[color=#4499ff][u]https://benchmark.waverian.com[/u][/color]'
            on_release: import webbrowser; webbrowser.open('https://benchmark.waverian.com')
        Spacer
 ''')
