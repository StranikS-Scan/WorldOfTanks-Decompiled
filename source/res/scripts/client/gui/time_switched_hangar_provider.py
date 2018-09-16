# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/time_switched_hangar_provider.py
from datetime import datetime
from debug_utils import LOG_CURRENT_EXCEPTION

class IHangarProvider(object):

    def get(self):
        raise NotImplementedError


class TimeSwitchedHangarProvider(IHangarProvider):

    def __init__(self, data):
        try:
            self.__hangarOne = data['hangarOne']
            self.__hangarTwo = data['hangarTwo']
            self.__timeOne = datetime.strptime(data['timeOne'], '%H:%M').time()
            self.__timeTwo = datetime.strptime(data['timeTwo'], '%H:%M').time()
            if self.__timeOne > self.__timeTwo:
                self.__timeOne, self.__timeTwo = self.__timeTwo, self.__timeOne
                self.__hangarOne, self.__hangarTwo = self.__hangarTwo, self.__hangarOne
        except ValueError:
            LOG_CURRENT_EXCEPTION()

    def get(self):
        currentTime = datetime.today().time()
        return self.__hangarOne if self.__timeOne <= currentTime < self.__timeTwo else self.__hangarTwo
