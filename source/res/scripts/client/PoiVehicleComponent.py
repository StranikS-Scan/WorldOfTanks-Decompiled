# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PoiVehicleComponent.py
from __future__ import absolute_import
import CGF
from PoiBaseComponent import PoiBaseComponent
from points_of_interest.components import PoiVehicleStateComponent

class PoiVehicleComponent(PoiBaseComponent):

    def __init__(self):
        super(PoiVehicleComponent, self).__init__()
        self.__isDead = False

    def onDestroy(self):
        if self._poiGameObject:
            self._poiGameObject.removeComponent(PoiVehicleStateComponent)
        self.__isDead = True
        super(PoiVehicleComponent, self).onDestroy()

    def _onAvatarReady(self):
        if not self.__isDead:
            queue = CGF.CommandQueue(self.spaceID)
            queue.removeComponent(self._poiGameObject, PoiVehicleStateComponent)
            queue.createComponent(self._poiGameObject, PoiVehicleStateComponent, self.pointID)
