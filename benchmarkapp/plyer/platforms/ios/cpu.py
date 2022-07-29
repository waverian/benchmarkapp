'''
Module of iOS API for plyer.cpu.
'''

from plyer.facades import CPU
from plyer.utils import whereis_exe
from pyobjus import autoclass
from pyobjus.dylib_manager import load_framework, INCLUDE
from plyer.facades import UniqueID
 
load_framework(INCLUDE.Foundation)
UIDevice = autoclass('UIDevice')
NSProcessInfo = autoclass('NSProcessInfo')
processInfo = NSProcessInfo.processInfo()
import os
import platform
# print(os.environ)
# print(platform.architecture())
# print('ProcessName: ', processInfo.processName.cString())
# print('HostName: ', processInfo.hostName.cString())
# print('OS Version: ', processInfo.operatingSystemVersionString.cString())
# print('ProcessorCount: ', processInfo.processorCount)
currentDevice = UIDevice.currentDevice()
# print('DeviceName: ', currentDevice.name.cString())
# print('SystemName: ', currentDevice.systemName.cString())
# print('UI Idiom: ', currentDevice.userInterfaceIdiom)
# print('Orientation: ', currentDevice.orientation)
# print('SystemVersion: ', currentDevice.systemVersion.cString())
import utils
# utils.OSVERSION = currentDevice.systemVersion.cString()
# print('DeviceModel ', currentDevice.model.cString())
# print('LocalizedModel: ', currentDevice.localizedModel.cString())
# print(currentDevice.identifierForVendor.UUIDString().cString())
# print('BatteryState:', currentDevice.batteryState)
 
class iOSCPU(CPU):
    '''
    Implementation of MacOS CPU API.
    '''

    @staticmethod
    def _sockets():
        return

    def _physical(self):
        # cores
        return processInfo.processorCount

    def _logical(self):
        # cores * threads
        return processInfo.activeProcessorCount

    @staticmethod
    def _cache():
        return

    @staticmethod
    def _numa():
        return

    @staticmethod
    def _name():
        return os.uname().version[-5:]

    @staticmethod
    def _architecture():
        import platform
        return platform.architecture()[0]

    @staticmethod
    def _features():
        return []

def instance():
    '''
    Instance for facade proxy.
    '''
    return iOSCPU()
