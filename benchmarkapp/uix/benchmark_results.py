from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

class BenchmarkResults(BoxLayout):
    Builder.load_string('''
#:import LargeTextScroll uix.widgets.largetextscroll.LargeTextScroll
#:import utils utils
#:import __main__ __main__

<ImgButt@ButtonBehavior+Image>
    size_hint_x: None
    width: self.height

<LeftLabel@Label>
    text_size: self.size
    font_size: sp(12)
    halign: 'left'
    valign: 'middle'

<MidLabel@Label>
    text_size: self.size
    halign: 'center'
    valign: 'middle'

<Topic@BoxLayout>
    text: ''
    size_hint_y: None
    height: dp(36)
    canvas.before:
        Color
            rgba: .3, .5, .7, 1
        Rectangle
            pos: self.pos
            size: self.size
    Label
        font_size: sp(16)
        text_size: self.size
        text: root.text
        valign: 'middle'
        halign: 'center'

<Separator@Widget>
    size_hint_y: None
    height: dp(.5)
    canvas.before:
        Color:
            rgba: 1, 1, 1, .5
        Rectangle:
            pos: self.pos
            size: self.size

<ResultItem@BoxLayout>
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    text: ''
    value: ''
    value1: ''
    value2: ''
    value3: ''
    loop_hash: ''
    BoxLayout:
        size_hint_y: None
        height: max(dp(32), self.minimum_height)
        LeftLabel
            text: root.loop_hash 
            size_hint_x: None
            width: dp(22)
        LeftLabel
            font_size: lft_lbl.font_size
            text: root.text
            size_hint_x: None
            width: max(dp(150), root.width/5)
            # color: 0, 0, 0, 1
            # canvas.before:
            #     Color
            #         rgba: 1, 1, 1, 1
            #     Rectangle:
            #         size: self.size
            #         pos: self.pos
        Widget
            size_hint_x: None
            width: dp(2)
        LeftLabel
            id: lft_lbl
            size_hint_x: None if not root.value1 else 1
            width: dp(200)
            text: root.value
        LeftLabel
            text: root.value1
        LeftLabel
            text: root.value2
        LeftLabel
            text: root.value3
    Separator

<ResultItemE@BoxLayout>
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    text: ''
    value: ''
    BoxLayout:
        size_hint_y: None
        height: self.minimum_height
        Widget:
            size_hint_x: None
            width: dp(22)
        LeftLabel:
            id: lft_label
            text: root.text
            size_hint_x: None
            width: max(dp(150), root.width/5)
        Label
            id: lbl_version
            font_size: lft_label.font_size
            size_hint_y: None
            height: self.texture_size[1] + dp(20)
            text_size: self.width, None
            text: root.value
    Separator


<Header@BoxLayout>
    size_hint_y: None
    height: dp(45)
    canvas.before:
        Color
            rgba: .3, .5, .7, 1
        Rectangle
            pos: self.pos
            size: self.size
    orientation: 'vertical'
    text: ''
    value: ''
    value1: ''
    value2: ''
    value3: ''
    BoxLayout:
        MidLabel
            text: root.text
            size_hint_x: None
            width: dp(120)
        MidLabel
            text: root.value
        MidLabel
            text: root.value1
        MidLabel
            text: root.value2
            size_hint_x: None if not self.text else 1
            width: 0
        MidLabel
            text: root.value3
            size_hint_x: None if not self.text else 1
            width: 0
    Separator


<BenchmarkResults>
    BoxLayout
        padding: dp(9)
        orientation: 'vertical'
        Button:
            text: 'Start Benchmark' if not app._benchmark_running else 'Running Benchmark'
            size_hint_y: None
            height: dp(45)
            disabled: app._benchmark_running
            on_release:
                # lbl_singlecore.text = '00723'
                br = app._benchmark_running
                if not br: app.run_benchmark()
                if br: app.stop_benchmark()
        BoxLayout
            #padding: dp(9)
            spacing: dp(9)
            orientation: 'vertical'
            ProgressBar:
                min: 0
                max: 100
                value: app.progress
                size_hint_y: None
                height: dp(22)
            BoxLayout
                size_hint_y: None
                height: dp(45)
                Label
                    text: app.progress_message# if not app.results else ''
                    text_size: self.size
                ImgButt
                    source: 'data/theme/blue/images/' + ('copy.png')
                    on_release:
                        data = app.get_formatted_result()
                        from kivy.core.clipboard import Clipboard
                        Clipboard.copy(str(data))
                        utils.make_toast('Copied to clipboard.')
                ImgButt
                    source: 'data/theme/blue/images/' + ('save.png' if utils.is_desktop else 'share.png')
                    on_release:
                        data = app.get_formatted_result()
                        if data and utils.is_desktop:\
                            utils.save_data(str(data))
                        if data and not utils.is_desktop:\
                            utils.do_share(data, 'LFK Benchmark Results')
            ScrollView
                BoxLayout
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    Topic
                        text: "LFK Benchmark Results"
                    BoxLayout
                        size_hint_y: None
                        height: lbl_singlecore.texture_size[1] + dp(20)
                        Label
                            id: lbl_singlecore
                            font_size: self.width/3
                            color: 0, 0, 0, 1
                            text: f'{app.result["singlecore_results"]:05.0f}' if app.result else ''
                            canvas.before:
                                Rectangle:
                                    size: self.size
                                    pos: self.pos
                        Label
                            id: lbl_multicore
                            font_size: self.width/3
                            text: f'{app.result["multicore_results"]:05.0f}' if app.result else ''
                    Separator
                    BoxLayout
                        size_hint_y: None
                        height: dp(24)
                        Label
                            font_size: sp('18')
                            text: "Single Core"
                        Label
                            font_size: sp('18')
                            text: "Multi Core"
                    Separator
                    ResultItem
                        text: 'Benchmark Version'
                        value: f'{app.result["version"]}' if app.result else ''
                    ResultItem
                        text: 'App Version'
                        value: f'{__main__.__version__}' if app.result else ''
                    ResultItem
                        text: 'Date'
                        value: f'{app.result["date"]}' if app.result else ''
                    ResultItemE
                        text: 'Compiler'
                        value: f'{app.result["compiler"]}' if app.result else ''
                    ResultItem
                        text: 'Core Count'
                        value: f'{app.result["core_count"]}' if app.result else ''
                    Header:
                        text: ' '
                        value: 'Device Details'
                        value1: ''
                    ResultItem
                        text: 'OS Name'
                        value: f'{utils.OSNAME}'
                    ResultItemE
                        text: 'Kernel Version'
                        value: utils.OSVERSION
                    Separator
                    # ResultItem
                    #     text: 'Device Name'
                    #     value: f'{utils.DEVICE}'
                    ResultItem
                        text: 'CPU'
                        value: f'{utils.CPU.name}'
                    ResultItem
                        text: 'ARCH'
                        value: f'{utils.CPU.architecture}'
                    ResultItemE
                        text: 'Features'
                        value: ', '.join(utils.CPUFEATURES)
                    Header:
                        text: ' '
                        value: 'Optimised'
                        value1: 'Non Optimised'
                    Header:
                        text: 'MFLOPS'
                        value: 'Single Core'
                        value1: 'Multi Core'
                        value2: 'Single Core'
                        value3: 'Multi Core'
                    ResultItem
                        id: result_maximum
                        text: 'Maximum'
                    ResultItem
                        id: result_average
                        text: 'Average'
                    ResultItem
                        id: result_geometric
                        text: 'Geometric'
                    ResultItem
                        id: result_harmonic
                        text: 'Harmonic'
                    ResultItem
                        id: result_minimum
                        text: 'Minimum'
                    Header:
                        text: 'LOOP #'
                        value: 'Single Core'
                        value1: 'Multi Core'
                        value2: 'Single Core'
                        value3: 'Multi Core'
                    BoxLayout
                        id: kernel_results
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
''')
