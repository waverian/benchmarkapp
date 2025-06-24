'''Monkey patch stuff:

This allows us to maintain our own version methods
patched for our use case working with upstream stable.
'''

import os
import subprocess as sp
import time
import plyer.platforms.linux.filechooser as filechooser
from distutils.spawn import find_executable as which
from utils import get_system_env


class SubprocessFileChooser:
    '''A file chooser implementation that allows using
    subprocess back-ends.
    Normally you only need to override _gen_cmdline, executable,
    separator and successretcode.
    '''

    executable = ""
    '''The name of the executable of the back-end.
    '''

    separator = "|"
    '''The separator used by the back-end. Override this for automatic
    splitting, or override _split_output.
    '''

    successretcode = 0
    '''The return code which is returned when the user doesn't close the
    dialog without choosing anything, or when the app doesn't crash.
    '''

    path = None
    multiple = False
    filters = []
    preview = False
    title = None
    icon = None
    show_hidden = False

    def __init__(self, *args, **kwargs):
        self._handle_selection = kwargs.pop(
            'on_selection', self._handle_selection
        )

        # Simulate Kivy's behavior
        for i in kwargs:
            setattr(self, i, kwargs[i])

    @staticmethod
    def _handle_selection(selection):
        '''
        Dummy placeholder for returning selection from chooser.
        '''
        return selection

    _process = None

    def _get_local_url(self, selection):
        if selection[0].startswith('/'):
            return selection

        if not selection[0].startswith('file://'):
            url = selection[0]
            import sh
            string = sh.dbus_send( '--session', '--print-reply', '--type=method_call', '--dest=org.kde.KIOFuse', '/org/kde/KIOFuse', 'org.kde.KIOFuse.VFS.mountUrl', f'string:{url}')
            string.split('string "')[1][:-1]
            protocol = url.split('://')[0]
            mount_point = string.split(protocol)[0].split('string "')[1]
        for i, url in enumerate(selection):
            if url.startswith('file://'):
                selection[i] = url.split('file://')[1]
            else:
                # The method is extremely slow use mount point instead
                url_split = url.split('://')
                selection[i] = '/'.join([mount_point[:-1], *url_split])
        return selection

    def _run_command(self, cmd, is_selection=True):
        env = get_system_env()
        self._process = sp.Popen(cmd, stdout=sp.PIPE, env=env)
        while True:
            ret = self._process.poll()
            if ret is not None:
                if ret == self.successretcode:
                    out = self._process.communicate()[0].strip().decode('utf8')
                    self.selection = self._split_output(out)
                    if not is_selection:
                        return self.selection[1]
                    self.selection = self._get_local_url(self.selection)
                    self._handle_selection(self.selection)
                    return self.selection
                else:
                    return None
            time.sleep(0.1)

    def _split_output(self, out):
        '''This methods receives the output of the back-end and turns
        it into a list of paths.
        '''
        return out.split(self.separator)

    def _gen_cmdline(self):
        '''Returns the command line of the back-end, based on the current
        properties. You need to override this.
        '''
        raise NotImplementedError()

    def run(self):
        return self._run_command(self._gen_cmdline())



class KDialogFileChooser(SubprocessFileChooser):
    '''A FileChooser implementation using KDialog (on GNU/Linux).

    Not implemented features:
    * show_hidden
    * preview
    '''

    executable = "kdialog"
    separator = "\n"
    successretcode = 0

    def _gen_cmdline(self):
        cmdline = [which(self.executable)]

        filt = []
        for f in self.filters:
            if isinstance(f, str):
                filt += [f]
            else:
                filters = ''
                for ext in self.filters:
                    exts = ''
                    for y in ext[1:]:
                        exts += f' {y};'
                    x = f'{ext[0]} ({exts})|'
                    filters += x
                filt = [filters[:-1]]

        if self.mode == "dir":
            cmdline += [
                "--getexistingdirectory",
                (self.path if self.path else os.path.expanduser("~"))
            ]
        elif self.mode == "save":
            cmdline += [
                "--getsavefilename",
                (self.path if self.path else os.path.expanduser("~")),
                " ".join(filt)
            ]
        else:
            cmdline += [
                "--getopenurl",
                (self.path if self.path else os.path.expanduser("~")),
                " ".join(filt)
            ]
        if self.multiple:
            cmdline += ["--multiple", "--separate-output"]
        if self.title:
            cmdline += ["--title", self.title]
        if self.icon:
            cmdline += ["--icon", self.icon]

        return cmdline

class ZenityFileChooser(SubprocessFileChooser):
    '''A FileChooser implementation using Zenity (on GNU/Linux).

    Not implemented features:
    * show_hidden
    * preview
    '''

    executable = "zenity"
    separator = "|"
    successretcode = 0

    def _gen_cmdline(self):
        cmdline = [
            which(self.executable),
            "--file-selection"]
        if self.title:
            cmdline += ["--title", self.title]
        if self.multiple:
            cmdline += ["--multiple"]

        if self.mode == "save":
            cmdline += ["--save"]
        elif self.mode == "dir":
            cmdline += ["--directory"]
        if self.path:
            cmdline += ["--filename", self.path]
        if self.icon:
            cmdline += ["--icon", self.icon]
        for f in self.filters:
            if isinstance(f, str):
                cmdline += ["--file-filter", f]
            else:
                cmdline += [
                    "--file-filter",
                    "{name} | {flt}".format(name=f[0], flt=" ".join(f[1:]))
                ]
        return cmdline


filechooser.CHOOSERS['kde'] = KDialogFileChooser
filechooser.CHOOSERS['gnome'] = ZenityFileChooser

from plyer.platforms.linux.filechooser import LinuxFileChooser
default_file_selection_dialog = LinuxFileChooser._file_selection_dialog

def patched_file_selection_dialog(self, **kwargs):
    LinuxFileChooser._file_selection_dialog = default_file_selection_dialog
    try:
        self._file_selection_dialog(**kwargs)
    except OSError:
        from kivy.clock import Clock
        from .. import make_toast, load_screen
        make_toast("Cannot find file provider! Please install `zenity` package.")

        on_selection = kwargs['on_selection']
        Clock.schedule_once(lambda dt: load_screen('FilechooserScreen', kwargs={'on_selection': on_selection}), 1.5)
    finally:
        LinuxFileChooser._file_selection_dialog = patched_file_selection_dialog


LinuxFileChooser._file_selection_dialog = patched_file_selection_dialog
