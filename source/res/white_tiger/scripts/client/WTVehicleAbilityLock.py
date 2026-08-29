# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleAbilityLock.py
import BigWorld
from items import vehicles
from script_component.DynamicScriptComponent import DynamicScriptComponent
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.status_notifications.sn_items import WTTimerViewState

class WTVehicleAbilityLock(DynamicScriptComponent):
    SILENCE_START = 'SILENCE_START'
    SILENCE_END = 'SILENCE_END'

    def __init__(self):
        super(WTVehicleAbilityLock, self).__init__()
        self.__guiFeedback = self.entity.guiSessionProvider.shared.feedback
        self.__equipment = None
        if self.equipmentID > 0:
            self.set_equipmentID(self.equipmentID)
            self.__update()
        return

    def onDestroy(self):
        self.__update()
        self.__equipment = None
        super(WTVehicleAbilityLock, self).__init__()
        return

    def set_equipmentID(self, prev):
        if self.equipmentID == prev:
            return
        self.__equipment = vehicles.g_cache.equipments().get(self.equipmentID)

    def set_finishTime(self, prev):
        if self.finishTime == prev:
            return
        self.__update()

    def set_lockedEquipmentCDs(self, prev):
        if self.lockedEquipmentCDs != prev:
            self.entity.wtAbilitiesManager.onEquipmentLocked(self.lockedEquipmentCDs['isLocked'], self.lockedEquipmentCDs['cds'])

    def __update(self):
        if self.__equipment is None:
            return
        duration = self.finishTime - BigWorld.serverTime()
        isShown = duration > 0
        if self.__equipment and self.__equipment.name == 'wt_impulse_mod_a':
            self.__updateSilence(isShown, duration)
            return
        else:
            return

    def __updateSilence(self, isShown, duration):
        self.__updateNotificationTimer(isShown, duration)
        self.__updateInGameMessage(isShown)

    def __updateNotificationTimer(self, isShown, duration):
        if self.entity.id != BigWorld.player().inputHandler.ctrl.curVehicleID:
            return
        value = WTTimerViewState(isShown, duration, self.finishTime)
        self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_SILENCE, value, vehicleID=self.entity.id)

    def __updateInGameMessage(self, isShown):
        if self.entity.id != BigWorld.player().inputHandler.ctrl.curVehicleID:
            return
        if isShown:
            self.entity.guiSessionProvider.shared.messages.onShowVehicleMessageByKey(self.SILENCE_START)
        else:
            self.entity.guiSessionProvider.shared.messages.onShowVehicleMessageByKey(self.SILENCE_END)
