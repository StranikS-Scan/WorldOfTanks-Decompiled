# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PoiCaptureBlockerComponent.py
from __future__ import absolute_import
import logging
import CGF
from PoiBaseComponent import PoiBaseComponent
from helpers import fixed_dict
from points_of_interest.components import PoiCaptureBlockerStateComponent
from points_of_interest_shared import PoiBlockReasons
_logger = logging.getLogger(__name__)

class PoiCaptureBlockerComponent(PoiBaseComponent):

    def onDestroy(self):
        if self._poiGameObject is not None and self._poiGameObject.valid:
            self._poiGameObject.removeComponent(PoiCaptureBlockerStateComponent)
        super(PoiCaptureBlockerComponent, self).onDestroy()
        return

    def set_blockReasons(self, prev):
        stateComponent = self._poiGameObject.findWrite(PoiCaptureBlockerStateComponent)
        if stateComponent:
            stateComponent.blockReasons = self.__getBlockReasons()

    def _onAvatarReady(self):
        if self._poiGameObject is not None and self._poiGameObject.valid:
            blockReasons = self.__getBlockReasons()
            stateComponent = self._poiGameObject.findWrite(PoiCaptureBlockerStateComponent)
            if stateComponent:
                stateComponent.blockReasons = blockReasons
                return
            queue = CGF.CommandQueue(self.spaceID)
            queue.createComponent(self._poiGameObject, PoiCaptureBlockerStateComponent, self.pointID, blockReasons)
        return

    def __getBlockReasons(self):
        return tuple((fixed_dict.getStatusWithTimeInterval(reason, PoiBlockReasons) for reason in self.blockReasons))
