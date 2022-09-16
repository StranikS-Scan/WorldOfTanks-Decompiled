# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PoiVehicleComponent.py
from PoiBaseComponent import PoiBaseComponent
from points_of_interest.components import PoiVehicleStateComponent

class PoiVehicleComponent(PoiBaseComponent):

    def onDestroy(self):
        self._poiGameObject.removeComponentByType(PoiVehicleStateComponent)
        super(PoiVehicleComponent, self).onDestroy()

    def _onAvatarReady(self):
        self._poiGameObject.createComponent(PoiVehicleStateComponent, self.pointID)
