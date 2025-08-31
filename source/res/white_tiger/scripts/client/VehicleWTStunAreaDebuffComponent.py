# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/VehicleWTStunAreaDebuffComponent.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from white_tiger.gui.gui_constants import FEEDBACK_EVENT_ID
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from items import vehicles
from gui.battle_control import avatar_getter
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playStunAreaHunterVO
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.status_notifications.sn_items import StunAreaTimerViewState

class VehicleWTStunAreaDebuffComponent(DynamicScriptComponent):

    def __init__(self):
        super(VehicleWTStunAreaDebuffComponent, self).__init__()
        self.__guiFeedback = self.entity.guiSessionProvider.shared.feedback
        self.__effectDuration = self.__getEffectDuration()
        self.__updateMarker(self.isDebuffActive)

    def onDestroy(self):
        self.__updateMarker(False)
        super(VehicleWTStunAreaDebuffComponent, self).__init__()

    def set_isDebuffActive(self, prev):
        if self.isDebuffActive != prev:
            isShown = False
            if self.entity.health > 0:
                isShown = self.isDebuffActive
            self.__updateMarker(isShown)
            self.__updateNotificationTimer(isShown)
            if self.isDebuffActive and self.entity.health > 0:
                self.__playVoiceOver()

    def __updateMarker(self, isShown):
        self.__guiFeedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.WT_VEHICLE_STUN_AREA_DEBUFF, self.entity.id, {'isShown': isShown,
         'duration': self.__effectDuration})

    def __updateNotificationTimer(self, isShown):
        value = StunAreaTimerViewState(isShown, self.__effectDuration, BigWorld.serverTime() + self.__effectDuration)
        self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_STUN_AREA, value, vehicleID=self.entity.id)

    def __playVoiceOver(self):
        vehicleID = avatar_getter.getPlayerVehicleID()
        if vehicleID == self.entity.id:
            playStunAreaHunterVO()

    def __getEffectDuration(self):
        equipmentID = vehicles.g_cache.equipmentIDs().get('builtinStunArea_wt')
        equipment = vehicles.g_cache.equipments()[equipmentID]
        return equipment.effectDuration
