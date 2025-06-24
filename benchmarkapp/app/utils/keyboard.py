'''Keyboard utils
'''
from utils import go_back_in_history#, go_full_screen


def hook_keyboard(*args):
    from kivy.base import EventLoop
    EventLoop.window.bind(on_keyboard=_hook_keyboard)


def _hook_keyboard(window, key, *largs):
    # print('keyboard ays :', key, *largs )
    modifiers = largs[2]
    # if key == 13 and  'alt' in modifiers:
    #     go_full_screen()
    #     return True
    if key == 27:
        # do what you want,
        # return True for stopping the propagation to widgets.
        # indicating we consumed the event.
        go_back_in_history()
        return True
    return False

def refocus_window():
    from kivy.utils import platform
    if platform != "android":
       return

    from android import activity
    from android.runnable import run_on_ui_thread

    @run_on_ui_thread
    def fix():
        activity._activity.onWindowFocusChanged(False)
        activity._activity.onWindowFocusChanged(True)
    
    fix()