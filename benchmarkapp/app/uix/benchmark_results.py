from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.factory import Factory

class BenchmarkResults(BoxLayout):
    Builder.load_string('''
#:import LargeTextScroll uix.widgets.largetextscroll.LargeTextScroll
#:import utils utils
#:import __main__ __main__

<LeftLabel@Label>
    text_size: self.size
    font_size: sp(12)
    halign: 'left'
    valign: 'middle'

<MidLabel@Label>
    text_size: self.size
    halign: 'center'
    valign: 'middle'

<Topic@Label>
    text: ''
    bg_color: .3, .5, .7, 1
    size_hint_y: None
    height: dp(36)
    canvas.before:
        Color
            rgba: root.bg_color
        Rectangle
            pos: self.pos
            size: self.size
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
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size

<ResultItem@BoxLayout>
    orientation: 'vertical'
    size_hint_y: None
    height: dp(32)
    text: ''
    value: ''
    value1: ''
    value2: ''
    value3: ''
    loop_hash: ''
    BoxLayout:
        LeftLabel
            text: root.loop_hash
            size_hint_x: None
            width: dp(22)
        LeftLabel
            font_size: lft_lbl.font_size
            text: root.text
            size_hint_x: None
            width: max(dp(160), root.width/5)
        Widget
            size_hint_x: None
            width: dp(2)
        LeftLabel
            id: lft_lbl
            # text_size: max(dp(70), self.width), self.height
            size_hint_x: None if not root.value1 else 1
            width: dp(200)
            text: root.value
        LeftLabel
            # text_size: max(dp(70), self.width), self.height
            text: root.value1
        LeftLabel
            # text_size: max(dp(70), self.width), self.height
            text: root.value2
        LeftLabel
            # text_size: max(dp(70), self.width), self.height
            text: root.value3
    Separator

<ResultItemE@BoxLayout>
    orientation: 'vertical'
    size_hint_y: None
    text: ''
    value: ''
    BoxLayout:
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
            text: root.value
            # size_hint_y: None
            text_size: max(dp(150), self.width), None
            valign: 'middle'
            pos_hint: {'center_y': .5}
            on_texture_size:
                def _set_height(*agrs): root.height = self.height = args[1][1] + dp(10)
                if hasattr(root, '_sched_height'): Clock.unschedule(root._sched_height)
                root._sched_height = Clock.schedule_once(_set_height, .25)
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
        Label
            text: root.value3
            size_hint_x: None if not self.text else 1
            width: 0
    Separator

<Score@VBoxLayout>
    result: {}
    optimized: 'non_optimized'
    on_result:
        Clock.schedule_once(lambda dt: app.benchmark_results.on_result(self, args[1]), .1)
    Topic
        id: topic
        text: (root.optimized.capitalize().replace('_', ' '), root.optimized)[0]
    Label
        id: overall_score
        font_size: min(sp(200), (root.width/2)/2)
        size_hint_y: None
        height:  min(dp(200), (root.width/2)/1.5)
        Label
            pos: overall_score.pos
            size: overall_score.width, overall_score.height/4
            font_size: sp('18')
            text: 'Overall Score'
    Separator
    BoxLayout
        size_hint_y: None
        height:  overall_score.font_size
        Label
            id: lbl_single_core
            font_size: self.height/1.5
            text_size: self.size
            valign: 'top'
            halign: 'center'
            color: 0, 0, 0, 1
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                Rectangle:
                    size: self.size
                    pos: self.pos
            Label
                color: lbl_single_core.color
                pos: lbl_single_core.pos
                size: lbl_single_core.width, lbl_single_core.height/4
                font_size: sp('18')
                id: single_core_ratio
        Label
            id: lbl_multi_core
            font_size: self.height/1.5
            text_size: self.size
            valign: 'top'
            halign: 'center'
            Label
                pos: lbl_multi_core.pos
                size: lbl_multi_core.width, lbl_multi_core.height/4
                font_size: sp('18')
                id: multi_core_ratio
    BoxLayout
        size_hint_y: None
        height: dp(24)
        Label
            font_size: sp('18')
            text: "Single Core"
            color: lbl_single_core.color
            canvas.before:
                Rectangle:
                    size: self.size
                    pos: self.pos
        Label
            font_size: sp('18')
            text: "Multi Core"
    Separator
    BoxLayout
        size_hint_y: None
        height:  overall_score.font_size
        Label
            id: lbl_quad_core
            font_size: lbl_single_core.font_size
            Label
                pos: lbl_quad_core.pos
                size: lbl_quad_core.width, lbl_quad_core.height/4
                font_size: sp('18')
                id: quad_core_ratio
        Label
            id: lbl_workstation
            font_size: lbl_single_core.font_size
            color: 0, 0, 0, 1
            canvas.before:
                Rectangle:
                    size: self.size
                    pos: self.pos
            Label
                color: lbl_workstation.color
                pos: lbl_workstation.pos
                size: lbl_workstation.width, lbl_workstation.height/4
                font_size: sp('18')
                id: workstation_ratio
    # Separator
    BoxLayout
        size_hint_y: None
        height: dp(24)
        Label
            font_size: sp('18')
            text: "Quad Core"
        Label
            font_size: sp('18')
            text: "Workstation"
            color: lbl_workstation.color
            canvas.before:
                Rectangle:
                    size: self.size
                    pos: self.pos
    Separator
    Topic
        id: resu
        ResultItem
            pos: resu.pos
            size: resu.width, resu.height
            text: topic.text
            value: "Single Core"
            value1: "Multi Core"
            value2: "Quad Core"
            value3: "Work Station"
    ResultItem
        id: result_maximum
    ResultItem
        id: result_average
    ResultItem
        id: result_geometric
    ResultItem
        id: result_harmonic
    ResultItem
        id: result_minimum
    Separator
    Topic
        id: topic_kernel
        ResultItem
            text: '#: Kernel Name'
            size: topic_kernel.size
            pos: topic_kernel.pos
    VBoxLayout
        id: kernel_box

<DeviceDetails@StencilView>
    size_hint_y: None
    hide: True
    height: bl.height if not root.hide else 0
    VBoxLayout
        id: bl
        pos: root.pos
        width: root.width if not root.hide else 0
        Topic:
            text:  'Device Details'
        ResultItemE
            text: 'OS Name'
            value: f'{utils.OSNAME}'# if utils.OSNAME != 'To Be Filled By O.E.M.' else 'Unknown Device'
        ResultItemE
            text: 'Model Info'
            value: f'{utils.DEVICE}'
        ResultItemE
            text: 'Kernel Version'
            value: utils.OSVERSION
        ResultItemE
            text: 'App Version'
            value: f'{__main__.__version__}'

<BenchmarkDetails@VBoxLayout>
    result_type: 'current'
    result: {}
    historical: False
    # on_historical: print('Historical:', self.historical)
    Topic:
        text: 'Benchmark Details'
    ResultItemE
        text: 'Benchmark Version'
        value: f'{root.result["system_info"]["version_info"]}' if root.result else ''
    ResultItemE
        text: 'Date'
        value: f'{root.result["timestamp"]}' if root.result else ''
    ResultItemE
        text: 'Compiler'
        value: f'{root.result["system_info"]["compiler_info"]}' if root.result else ''
    FloatLayout:
        id: fl_comment
        size_hint_y: None
        height: dp(54)
        WTextInput
            id: ti_comment
            padding:dp(20), dp(9)
            hint_text: 'Enter Comment here'
            size: fl_comment.size
            pos: (-9000) if root.historical else fl_comment.x, fl_comment.y
            on_text_validate:
                if self.text: root.result["comment"] = self.text
        ResultItemE
            pos: (-9000) if not root.historical else fl_comment.x, fl_comment.y
            text: 'Comment'
            value: root.result["comment"] if root.result else ''
    ResultItemE
        text: 'Logical Cores'
        value: f'{root.result["system_info"]["cpu_core_count"]}' if root.result else ''
    ResultItemE
        text: 'CPU'
        value: root.result["system_info"]["cpu_name"] if root.result else ''

<BenchResults@VBoxLayout>
    result: {}
    historical: False
    DeviceDetails
        hide: root.historical
    BenchmarkDetails
        id: details
        historical: root.historical
        result: root.result or {}
    StencilView
        id: sv
        size_hint_y: None
        height: dp(0) if root.historical else vb.height
        VBoxLayout
            id: vb
            pos: sv.pos
            width: sv.width
            ResultItemE
                text: 'ARCH'
                value: f'{utils.CPU.architecture}'
            ResultItemE
                text: 'Features'
                value: ', '.join(utils.CPUFEATURES)
    Score
        optimized: 'non_optimized'
        result: root.result if root.result else {}
    Score
        optimized: 'optimized'
        result: root.result if root.result else {}

<BenchmarkResults>
    # size_hint_x: None
    Magnet
        duration: 0.1 if utils.is_desktop else 0
        BoxLayout
            size_hint_x: None
            # on_width: print('Benchmark results, Width: ', self.width, '<<<<')
            padding: dp(5)
            orientation: 'vertical'
            BoxLayout
                size_hint_y: None
                height: dp(45)
                MuseumButton:
                    text: 'Start Benchmark' if not app._benchmark_running else 'Running Benchmark'
                    disabled: app._benchmark_running
                    on_release:
                        # lbl_singlere.text = '00723'
                        br = app._benchmark_running
                        if not br: app.run_benchmark(comment=results.ids.details.ids.ti_comment.text, workstation=chk_workstation.active)
                        if br: app.stop_benchmark()
                CheckBox
                    id: chk_workstation
                    color: 5, 5, 5, 5
                    size_hint_x: None
                    width: self.height * 2.2
                    Label
                        pos: chk_workstation.pos
                        size: chk_workstation.width, dp(10)
                        text: 'Workstation'
            BoxLayout
                #padding: dp(9)
                spacing: dp(7)
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
                        font_size: sp(13)
                        text: app.progress_message if app.progress_message else 'uninitialized'
                        text_size: self.size
                        valign: 'middle'
                    CopySave
                        result: app.result
                WaverianScrollView
                    BenchResults
                        id: results
                        result: app.result
''')

    def on_result(self, root, result):
        app = App.get_running_app()
        if result:
            # print(root.optimized)
            # from pudb import set_trace; set_trace()
            optimized_path = root.result["full_result"][root.optimized]
            detailed_path = optimized_path["detailed"]

            root.ids.overall_score.text = f'{optimized_path["score"]:05.0f}'
            for core in ["single_core", "multi_core", "quad_core", 'workstation']:
                if detailed_path[core]:
                    root.ids[f'lbl_{core}'].text = f'{detailed_path[core]["score"]:05.0f}'
                    root.ids[f'{core}_ratio'].text = (f'{detailed_path[core]["ratio"]:04.01f}') + " x ratio"
                else:
                    root.ids[f'lbl_{core}'].text = 'N/A'
                    root.ids[f'{core}_ratio'].text = 'N/A'

            for item in ["maximum", "average", "geometric", "harmonic", "minimum"]:
                root.ids[f'result_{item}'].text = item.capitalize()
                root.ids[f'result_{item}'].value = f'{detailed_path["single_core"][item]:0.0f}'
                root.ids[f'result_{item}'].value1 = f'{detailed_path["multi_core"][item]:0.0f}'
                root.ids[f'result_{item}'].value2 = f'{detailed_path["quad_core"][item]:0.0f}'
                root.ids[f'result_{item}'].value3 = f'{detailed_path["workstation"][item]:0.0f}' if detailed_path["workstation"] and detailed_path["workstation"][item] else 'N/A'

            root.ids.kernel_box.clear_widgets()
            add_widget = root.ids.kernel_box.add_widget
            kernel_keys = app.kernel_keys


            for kernel in kernel_keys:
                result_item = Factory.ResultItem(
                        loop_hash = f'{kernel}.',
                        text = f'{kernel_keys[kernel]}',
                        value = f'{detailed_path["single_core"]["kernels"][int(kernel)-1]:0.0f}',
                        value1 = f'{detailed_path["multi_core"]["kernels"][int(kernel)-1]:0.0f}',
                        value2 = f'{detailed_path["quad_core"]["kernels"][int(kernel)-1]:0.0f}',
                        value3 = f'{detailed_path["workstation"]["kernels"][int(kernel)-1]:0.0f}' if detailed_path["workstation"] else 'N/A'
                    )
                add_widget(result_item)
