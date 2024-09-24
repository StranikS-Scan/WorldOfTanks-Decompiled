# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/ArenaObserverInfoComp7Component.py
import logging
import BigWorld
_logger = logging.getLogger(__name__)

class ArenaObserverInfoComp7Component(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(ArenaObserverInfoComp7Component, self).__init__()
        _logger.debug('__init__')

    def onDestroy(self):
        super(ArenaObserverInfoComp7Component, self).onDestroy()
        _logger.debug('onDestroy')

    def setNested_vehiclesInfo(self, changePath, oldValue):
        pass

    def setSlice_vehiclesInfo(self, changePath, oldValue):
        pass

    def setNested_poiInfo(self, changePath, oldValue):
        pass

    def setSlice_poiInfo(self, changePath, oldValue):
        pass

    def setNested_teamBasesInfo(self, changePath, oldValue):
        pass

    def setSlice_teamBasesInfo(self, changePath, oldValue):
        pass
