# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleInvisibilityDebuff.py
import BigWorld
import CGF
import functools
from GenericComponents import TransformComponent
from items import vehicles
from script_component.DynamicScriptComponent import DynamicScriptComponent
from white_tiger_common.wt_constants import InvisibilityState
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playVOInvisibilityModAStart, playVOInvisibilityModAStop, playVOInvisibilityModBStart

class WTVehicleInvisibilityDebuff(DynamicScriptComponent):

    def __init__(self):
        super(WTVehicleInvisibilityDebuff, self).__init__()
        self.__equipment = None
        return

    def onDestroy(self):
        self.__equipment = None
        super(WTVehicleInvisibilityDebuff, self).onDestroy()
        return

    def set_equipmentID(self, prev):
        if prev != self.equipmentID:
            self.__equipment = vehicles.g_cache.equipments().get(self.equipmentID)

    def set_debuffState(self, prev):
        if prev != self.debuffState and self.debuffState != InvisibilityState.DISABLED and self.__equipment is not None:
            self.__updateSound(self.__equipment.name)
        return

    def set_vehiclesData(self, prev):
        if self.debuffState == InvisibilityState.DISABLED:
            return
        else:
            for vehicleData in self.vehiclesData:
                isAlive = vehicleData['isAlive']
                prefabPath = self.__equipment.entrancePrefab if self.debuffState == InvisibilityState.ACTIVATED and isAlive else self.__equipment.escapePrefab
                if prefabPath is None:
                    return
                CGF.loadGameObject(prefabPath, self.spaceID, vehicleData['position'], functools.partial(self.__onLoaded, vehicleData['direction'], self.debuffState))

            return

    def _onAvatarReady(self):
        self.set_equipmentID(None)
        return

    def __onLoaded(self, rotation, onLoadState, go):
        if self.debuffState != onLoadState:
            CGF.removeGameObject(go)
            return
        transformComponent = go.findComponentByType(TransformComponent)
        if transformComponent:
            transformComponent.rotation = rotation

    def __updateSound(self, equipmentName):
        if BigWorld.player().id != self.entity.avatarID:
            return
        if equipmentName == 'wt_invisibility_mod_a':
            if self.debuffState == InvisibilityState.ACTIVATED:
                playVOInvisibilityModAStart()
            else:
                playVOInvisibilityModAStop()
        elif self.debuffState == InvisibilityState.ACTIVATED:
            playVOInvisibilityModBStart()
