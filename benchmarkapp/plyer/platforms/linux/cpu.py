'''
Module of Linux API for plyer.cpu.
'''

from collections import defaultdict
from os import listdir, uname
from os.path import join
from typing import List

from plyer.facades import CPU


class LinuxCPU(CPU):
    '''
    Implementation of Linux CPU API.
    '''

    def __init__(self):

        self._cpuinfo = defaultdict(list)

        with open('/proc/cpuinfo') as cpuinfo:

            for line in cpuinfo.readlines():
                entry = line.split(':', maxsplit=1)

                if len(entry) != 2:
                    continue

                self._cpuinfo[entry[0].strip()].append(entry[1].strip())

    def _get_cpuinfo(self, key: str) -> List[str]:
        if key not in self._cpuinfo:
            return []

        return self._cpuinfo[key]

    def _sockets(self):
        # count of unique CPU physical IDs
        return len(set(self._get_cpuinfo('physical id')))

    def _physical(self):
        # count of unique CPU core IDs
        return len(set(self._get_cpuinfo('core id')))

    def _logical(self):
        # count of all CPU core IDs
        return len(self._get_cpuinfo('core id'))

    @staticmethod
    def _cache():
        values = {key: 0 for key in ('L1', 'L2', 'L3')}
        cpu_path = join('/sys', 'devices', 'system', 'cpu')

        # get present cores from kernel device
        with open(join(cpu_path, 'present')) as fle:
            present = fle.read()
        present = present.strip().split('-')

        if len(present) == 2:
            present = range(int(present[1]) + 1)
        else:
            present = [present[0]]

        cores = ['cpu{}'.format(i) for i in present]
        for core in cores:
            indicies = [
                # get 'indexN' files from 'cache' folder assuming
                # the filename is in range index0 to index99
                # in case a wild 'index_whatevercontent' file appears
                fle for fle in listdir(join(cpu_path, core, 'cache'))
                if fle.startswith('index') and len(fle) <= len('index') + 2
            ]

            for index in indicies:
                index_type = join(cpu_path, core, 'cache', index, 'level')
                with open(index_type) as fle:
                    cache_level = fle.read().strip()
                values['L{}'.format(cache_level)] += 1
        return values

    @staticmethod
    def _numa():
        return

    def _name(self):

        for key in ('Hardware', 'model name'):

            values = self._get_cpuinfo(key)
            if not values:
                continue

            return values[0]

        # Fallback
        return 'Generic ' + uname().machine

    @staticmethod
    def _architecture():
        return uname().machine

    def _features(self):

        for key in ('flags', 'Features'):

            values = self._get_cpuinfo(key)
            if not values:
                continue

            return list(map(lambda it: it.strip(), values[0].split()))

        return []


def instance():
    '''
    Instance for facade proxy.
    '''
    return LinuxCPU()
