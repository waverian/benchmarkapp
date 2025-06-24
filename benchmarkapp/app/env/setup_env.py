'''
'''

import os


# ensure image is read by sdl2 first.
if "KCFG_KIVY_LOG_LEVEL" not in os.environ:
    os.environ["KCFG_KIVY_LOG_LEVEL"] = "debug"
os.environ["KIVY_IMAGE"] = "tex,dds,sdl2"

# Fix issues with touch pad being detected as a touch input.
if 'KCFG_INPUT_%(NAME)S' not in os.environ:
    os.environ['KCFG_INPUT_%(NAME)S'] = ''

# Disable kivy cli argument parsing.
if "KIVY_NO_ARGS" not in os.environ:
    os.environ["KIVY_NO_ARGS"] = "1"


# density = 2
# scale=.3
# dpi = 432
# os.environ['KIVY_METRICS_DENSITY'] = str(density * scale)
# os.environ['KIVY_DPI'] = str(dpi * scale)
# width = 2752

# from kivy.config import Config
# Config.set('graphics', 'width', str(int(width * scale)))
# # simulate with the android bar
# # FIXME should be configurable
# height = 2064
# Config.set('graphics', 'height', str(int(height * scale * density)))
# Config.set('graphics', 'fullscreen', '0')
# Config.set('graphics', 'show_mousecursor', '1')

# ref: https://github.com/kivy/kivy-ios/blame/master/kivy_ios/tools/templates/%7B%7B%20cookiecutter.project_name%20%7D%7D-ios/main.m#L35
if "KIVY_NO_CONFIG" in os.environ:
    os.environ.pop("KIVY_NO_CONFIG")
if "KIVY_NO_FILELOG" in os.environ:
    os.environ.pop("KIVY_NO_FILELOG")


from kivy.config import Config
Config.set('graphics', 'maxfps', '120')
Config.set('graphics', 'vsync', '1')
# Config.set('modules', 'monitor', '')
Config.set('kivy', 'log_level', 'debug')
Config.set('kivy','window_icon','data/icon.ico')


from kivy.utils import platform

# if "NO_SENTRY" not in os.environ:
#     # setup_sentry
#     from _version import __version__
#     os.environ["SENTRY_RELEASE"] = __version__
#     import sentry_sdk
#     from sentry_sdk.integrations.atexit import AtexitIntegration
#     from sentry_sdk.integrations.excepthook import ExcepthookIntegration
#     from sentry_sdk.integrations.dedupe import DedupeIntegration
#     from sentry_sdk.integrations.modules import ModulesIntegration
#     from sentry_sdk.integrations.logging import LoggingIntegration
#     sentry_sdk.init(
#         dsn="https://your_sentry_dsn_here",
#         traces_sample_rate=1.0,
#         default_integrations=False,
#         integrations=[
#             AtexitIntegration(),
#             ExcepthookIntegration(),
#             DedupeIntegration(),
#             ModulesIntegration(),
#             LoggingIntegration(),
#         ],
#     )

if platform == 'ios':
    from utils import ios_orientation

if platform == 'linux':
    from utils import patch_plyer_filechooser
