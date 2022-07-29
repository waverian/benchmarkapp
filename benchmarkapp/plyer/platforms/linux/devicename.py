'''
Module of Linux API for plyer.devicename.
'''

import socket
from plyer.facades import DeviceName


class LinuxDeviceName(DeviceName):
    '''
    Implementation of Linux DeviceName API.
    '''

    def _get_device_name(self):
        hostname = socket.gethostname()
        return hostname

    def _get_model_name(self):
        import platform
        return platform.node().split('_', 1)[1]


def instance():
    '''
    Instance for facade proxy.
    '''
    return LinuxDeviceName()
