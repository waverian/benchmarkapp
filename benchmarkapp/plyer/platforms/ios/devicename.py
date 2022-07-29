'''
Module of MacOSX API for plyer.devicename.
'''

import socket
from plyer.facades import DeviceName


class iOSDeviceName(DeviceName):
    '''
    Implementation of MacOSX DeviceName API.
    '''

    def _get_device_name(self):
        hostname = socket.gethostname()
        return hostname

    def _get_model_name(self):
        hostname = socket.gethostname().split('_', 1)[1]
        import os
        return hostname + '\nModel: ' + os.uname().machine



def instance():
    '''
    Instance for facade proxy.
    '''
    return iOSDeviceName()
