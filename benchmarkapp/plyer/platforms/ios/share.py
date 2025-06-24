# coding=utf-8
"""
Share
-----
"""

from plyer.facades import Share
from plyer import storagepath
from pyobjus import autoclass
from pyobjus.objc_py_types import NSSize, NSRect, NSPoint
from typing import Tuple

NSURL = autoclass('NSURL')
UIApplication = autoclass('UIApplication')
UIDevice = autoclass('UIDevice')
UIActivityViewController = autoclass('UIActivityViewController')
sharedApplication = UIApplication.sharedApplication()
UIcontroller = sharedApplication.keyWindow.rootViewController()
UIView = UIcontroller.view()

currentDevice = UIDevice.currentDevice()
iPhone = currentDevice.userInterfaceIdiom == 0
iPad = currentDevice.userInterfaceIdiom == 1
if iPad:
    val = NSRect()
    UINavigationController = autoclass('UINavigationController')
    uin = UINavigationController.alloc()

class IosShare(Share):

    def _write_data_to_file(self, data, out_file):
        with open(out_file, 'wb') as ofile:
            ofile.write(data)

    def _share_text(self, text: str, title: str,
        size: Tuple[int, int]=(32, 32),
        pos:Tuple[int, int]=(200, 200),
        arrow_direction:int=0):
        self._share_file(text, None, title,
            size=size, pos=pos, arrow_direction=arrow_direction)

    def _share_file(
        self, data: str, filename: str, title: str,
        size: Tuple[int, int]=(32, 32),
        pos:Tuple[int, int]=(200, 200),
        arrow_direction:int=0):

        if not data:
            return

        if filename:
            out_file = storagepath.get_home_dir() + '/Documents/' + filename
            self._write_data_to_file(data, out_file)
            URL = NSURL.fileURLWithPath_(out_file)
            data = URL

        import gc
        gc.collect()

        UIActivityViewController_instance = UIActivityViewController.alloc().init()
        activityViewController = UIActivityViewController_instance.initWithActivityItems_applicationActivities_([data], None)

        if iPad:
            from kivy.app import App
            app = App.get_running_app()

            # avc = UINavigationController.alloc().initWithRootViewController_(activityViewController)
            # print(dir(avc))
            # sheet = avc.sheetPresentationController()
            # print(dir(sheet))
            # sheet._detents = 
            activityViewController.modalPresentationStyle = 9# 9  is popover
            # activityViewController.preferredContentSize = val.size
            pc = activityViewController.popoverPresentationController()
            pc.permittedArrowDirections = 0
            pc.sourceView = UIView
            pc.sourceRect.origin = NSPoint(*pos)
            pc.sourceRect.size = NSSize(*size)
            UIcontroller.presentViewController_animated_completion_(activityViewController, True, None)
            # avc.release()
            activityViewController.release()
            UIActivityViewController_instance.release()
        else:
            UIcontroller.presentViewController_animated_completion_(activityViewController, True, None)
        gc.collect()



def instance():
    return IosShare()
