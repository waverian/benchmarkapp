'''
'''

import os
# ensure image is read by sdl2 first.
if "KCFG_KIVY_LOG_LEVEL" not in os.environ:
    os.environ["KCFG_KIVY_LOG_LEVEL"] = "debug"
os.environ["KIVY_IMAGE"] = "tex,dds,sdl2"
os.environ["KCFG_GRAPHICS_MAXFPS"] = '120'

# Fix issues with touch pad being detected as a touch input.
# if 'KCFG_INPUT_%(NAME)S' not in os.environ:
    # pass
    # os.environ['KCFG_INPUT_%(NAME)S'] = ''

# Disable kivy cli argument parsing.
if "KIVY_NO_ARGS" not in os.environ:
    os.environ["KIVY_NO_ARGS"] = "1"

# ref: https://github.com/kivy/kivy-ios/blame/master/kivy_ios/tools/templates/%7B%7B%20cookiecutter.project_name%20%7D%7D-ios/main.m#L35
if "KIVY_NO_CONFIG" in os.environ:
    os.environ.pop("KIVY_NO_CONFIG")
if "KIVY_NO_FILELOG" in os.environ:
    os.environ.pop("KIVY_NO_FILELOG")


from kivy.config import Config
Config.set('graphics', 'maxfps', '120')
Config.set('graphics', 'vsync', '0')
Config.set('kivy', 'log_level', 'debug')
Config.set('kivy','window_icon','data/icon.ico')


from kivy.utils import platform

if platform == 'ios':
    from utils import ios_orientation
    
if platform == 'linux':
    from utils import patch_plyer_filechooser