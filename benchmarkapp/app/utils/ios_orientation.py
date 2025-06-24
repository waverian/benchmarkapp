''' Listen and respond to ios orientation changes
'''

from kivy.app import App
from kivy.clock import mainthread, Clock
import ios
from pyobjus import autoclass, selector, protocol
from pyobjus.protocols import protocols
from kivy.logger import Logger
from utils import device_has_notch
import utils

UIDevice = autoclass('UIDevice')
CurrentDevice = UIDevice.currentDevice()

NSNotificationCenter = autoclass('NSNotificationCenter')

protocols["OrientationDelegates"] = {
    'OrientationChanged': ('v16@0:4@8', "v32@0:8@16")}


class iOSOrientationResponder(object):
    '''
    '''

    def __init__(self, *args, **kwargs):
        super(iOSOrientationResponder, self).__init__(*args, **kwargs)
        CurrentDevice.beginGeneratingDeviceOrientationNotifications()
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self,
            selector("OrientationChanged"),
            "UIDeviceOrientationDidChangeNotification",
            CurrentDevice)

    def stop_listening(self):
        CurrentDevice.stopGeneratingDeviceOrientationNotifications()

    def _show_statusbar(self, *args):
        utils.show_status_bar()

    @protocol('OrientationDelegates')
    def OrientationChanged(self, notification):
        app = App.get_running_app()
        orientation = notification.object().orientation
        if orientation == 5:
            return
        app.rotation = {
        1: 0,
        4: 90,
        2: 180,
        3: 270,
        5: 360,#flat/ Screen Up
        6: 360,#Face/Screen Down.
        }[orientation]

        Clock.unschedule(self._show_statusbar)
        Clock.schedule_once(self._show_statusbar, 1)

orientation_responder = iOSOrientationResponder()