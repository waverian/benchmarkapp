from collections import defaultdict
from typing import List

from plyer.facades import Processors


class LinuxProcessors(Processors):

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

    def _get_state(self):
        return {'Number_of_Processors': str(len(self._get_cpuinfo('core id')))}


def instance():
    return LinuxProcessors()
