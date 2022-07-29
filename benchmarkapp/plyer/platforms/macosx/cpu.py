'''
Module of MacOS API for plyer.cpu.
'''

from subprocess import Popen, PIPE
from plyer.facades import CPU
from plyer.utils import whereis_exe


class OSXCPU(CPU):
    '''
    Implementation of MacOS CPU API.
    '''

    @staticmethod
    def _sockets():
        return

    def _physical(self):
        # cores
        physical = None

        _physical = Popen(
            ['sysctl', '-n', 'hw.physicalcpu_max'],
            stdout=PIPE
        )
        output = _physical.communicate()[0].decode('utf-8').strip()
        if output:
            physical = int(output)
        return physical

    def _logical(self):
        # cores * threads
        logical = None

        _logical = Popen(
            ['sysctl', '-n', 'hw.logicalcpu_max'],
            stdout=PIPE
        )
        output = _logical.communicate()[0].decode('utf-8').strip()
        if output:
            logical = int(output)
        return logical

    @staticmethod
    def _cache():
        return

    @staticmethod
    def _numa():
        return

    @staticmethod
    def _name():
        name = Popen('sysctl -n machdep.cpu.brand_string'.split(' '),
            stdout=PIPE)
        name = name.communicate()[0].decode('utf-8').strip()
        return name

    @staticmethod
    def _architecture():
        architecture = Popen('uname -m'.split(' '),
            stdout=PIPE)
        architecture = architecture.communicate()[0].decode('utf-8').strip()
        return architecture

    @staticmethod
    def _features():
        features = Popen('sysctl -a'.split(' '),
            stdout=PIPE)
        features = features.communicate()[0].decode('utf-8').strip()
        features = [x.split('.')[-1].split(':')[0] for x in features.split('\n') if x.startswith('hw.optional') and x.endswith('1')]
        return features

def instance():
    '''
    Instance for facade proxy.
    '''
    import sys
    if whereis_exe('sysctl'):
        return OSXCPU()
    sys.stderr.write('sysctl not found.')
    return CPU()
