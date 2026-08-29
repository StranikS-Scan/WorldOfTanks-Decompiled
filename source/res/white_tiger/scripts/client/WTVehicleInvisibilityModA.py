# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleInvisibilityModA.py
import BigWorld
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from items import vehicles
from script_component.DynamicScriptComponent import DynamicScriptComponent
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playInvisibilityModASound
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.status_notifications.sn_items import WTTimerViewState

class WTVehicleInvisibilityModA(DynamicScriptComponent):

    def onDestroy(self):
        self.__setBinocularVisibility(False)
        super(WTVehicleInvisibilityModA, self).onDestroy()

    def set_finishTime(self, prev):
        value = WTTimerViewState(self.finishTime > 0, self.duration, self.finishTime)
        self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_BOSS_INVISIBILITY, value, vehicleID=self.entity.id)
        self.__setBinocularVisibility(self.finishTime > 0)
        playInvisibilityModASound(self.finishTime > 0)

    def __setBinocularVisibility(self, isVisible):
        if self.entity.avatarID != BigWorld.player().id:
            return
        elif BigWorld.isForwardPipeline():
            return
        else:
            binoculars = BigWorld.binoculars()
            if binoculars is None:
                return
            equipment = vehicles.g_cache.equipments().get(self.equipmentID)
            if isVisible:
                for effect in equipment.procedureEffects:
                    binoculars.loadConfig(effect)

            binoculars.setIsFlame(isVisible)
            binoculars.setIsDistortion(isVisible)
            return
