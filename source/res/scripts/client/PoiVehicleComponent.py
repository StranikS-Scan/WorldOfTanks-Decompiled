# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PoiVehicleComponent.py
from PoiBaseComponent import PoiBaseComponent
from points_of_interest.components import PoiVehicleStateComponent

class PoiVehicleComponent(PoiBaseComponent):

    def __init__(self):
        super(PoiVehicleComponent, self).__init__()
        self.__stateComponent = None
        self.__isDead = False
        return

    def onDestroy(self):
        self._poiGameObject.removeComponent(self.__stateComponent)
        self.__stateComponent = None
        self.__isDead = True
        super(PoiVehicleComponent, self).onDestroy()
        return

    def _onAvatarReady(self):
        if not self.__isDead:
            self.__stateComponent = self._poiGameObject.createComponent(PoiVehicleStateComponent, self.pointID)
