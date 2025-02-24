# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/indicator_items/indicators_storage.py
import logging
import Event
_logger = logging.getLogger(__name__)

class IndicatorsStorage(object):
    __slots__ = ('__storage', 'onNewItem')

    def __init__(self):
        super(IndicatorsStorage, self).__init__()
        self.__storage = dict()
        self.onNewItem = Event.Event()

    def get(self, name):
        return self.__storage.get(name, None)

    def add(self, name, indicatorMeta):
        if name in self.__storage:
            _logger.error('trying to add indicator meta(%s) multiple times', name)
            return
        self.__storage[name] = indicatorMeta
        self.onNewItem(name, indicatorMeta)

    def pop(self, name):
        self.__storage.pop(name, None)
        return


g_indicatorsStorage = IndicatorsStorage()
