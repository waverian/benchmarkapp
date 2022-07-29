'''
Module of Linux API for plyer.cpu.
'''
from collections import defaultdict
from os import listdir, uname
from os.path import join
from typing import List
from kivy.logger import Logger
from plyer.facades import CPU


class AndroidCPU(CPU):
    '''
    Implementation of Android CPU API.
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


    def _get_prop(self, prop):
        import subprocess
        try:
            proc1 = subprocess.Popen(['getprop'], stdout=subprocess.PIPE)
            proc2 = subprocess.Popen(['grep', prop], stdin=proc1.stdout,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            proc1.stdout.close() # Allow proc1 to receive a SIGPIPE if proc2 exits.
            out, err = proc2.communicate()
            Logger.debug(f'Plyer.cpu: out: {out}, err: {err}')
            out = out.decode('utf-8')

            name = out.split(':')[-1].strip()[1:-1]
            return name
        except Exception as err:
            Logger.debug(f'Plyer.CPU: {err}')
            return 'Unknown'

    def _sockets(self):
        # count of unique CPU physical IDs
        return len(set(self._get_cpuinfo('physical id'))) or 1

    def _physical(self):
        return len(set(self._get_cpuinfo('core id'))) or len(self._get_cpuinfo('processor'))

    def _logical(self):
        return len(self._get_cpuinfo('core id')) or len(self._get_cpuinfo('processor'))

    def _cache(self):
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
                with open(index_type, 'rb') as fle:
                    cache_level = fle.read().decode('utf-8').strip()
                values['L{}'.format(cache_level)] += 1
        return values

    @staticmethod
    def _numa():
        return

    def _name(self):
        return self._get_prop('ro.soc.model')

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
    return AndroidCPU()
