# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PoiCaptureBlockerComponent.py
import logging
import typing
from PoiBaseComponent import PoiBaseComponent
from helpers import fixed_dict
from points_of_interest.components import PoiCaptureBlockerStateComponent
from points_of_interest_shared import PoiBlockReasons
_logger = logging.getLogger(__name__)

class PoiCaptureBlockerComponent(PoiBaseComponent):

    def __init__(self):
        super(PoiCaptureBlockerComponent, self).__init__()
        self.__stateComponent = None
        return

    def onDestroy(self):
        if self._poiGameObject is not None and self._poiGameObject.isValid():
            self._poiGameObject.removeComponent(self.__stateComponent)
        self.__stateComponent = None
        super(PoiCaptureBlockerComponent, self).onDestroy()
        return

    def set_blockReasons(self, prev):
        if self.__stateComponent is not None:
            self.__stateComponent.blockReasons = self.__getBlockReasons()
        return

    def _onAvatarReady(self):
        if self._poiGameObject is not None and self._poiGameObject.isValid():
            blockReasons = self.__getBlockReasons()
            self.__stateComponent = self._poiGameObject.findComponentByType(PoiCaptureBlockerStateComponent)
            if self.__stateComponent:
                self.__stateComponent.blockReasons = blockReasons
                return
            self.__stateComponent = self._poiGameObject.createComponent(PoiCaptureBlockerStateComponent, self.pointID, blockReasons)
        return

    def __getBlockReasons(self):
        return tuple((fixed_dict.getStatusWithTimeInterval(reason, PoiBlockReasons) for reason in self.blockReasons))
