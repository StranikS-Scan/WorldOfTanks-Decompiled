# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleFactorAppliers.py
import BigWorld
import SoundGroups
from script_component.DynamicScriptComponent import DynamicScriptComponent
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from items import vehicles
from white_tiger.gui.gui_constants import FEEDBACK_EVENT_ID
from white_tiger.gui.battle_control.controllers.consumables.equipment_sound import playStunAreaHunterVO
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.status_notifications.sn_items import WTTimerViewState

class WTVehicleFactorAppliers(DynamicScriptComponent):
    _ABILITIES_NOTIFICATION_TIMER = {'wt_stun_area': (VEHICLE_VIEW_STATE.WT_STUN_AREA, WTTimerViewState),
     'wt_impulse_mod_a': (VEHICLE_VIEW_STATE.STUN, WTTimerViewState),
     'wt_stun_area_mod_a': (VEHICLE_VIEW_STATE.WT_STUN_AREA_MOD_A, WTTimerViewState),
     'wt_extractor_shot': (VEHICLE_VIEW_STATE.STUN, WTTimerViewState)}
    _ABILITIES_MARKERS = {'wt_stun_area': FEEDBACK_EVENT_ID.WT_VEHICLE_STUN_AREA_DEBUFF,
     'wt_stun_area_mod_a': FEEDBACK_EVENT_ID.WT_VEHICLE_STUN_AREA_MOD_A_DEBUFF,
     'wt_extractor_shot': FEEDBACK_EVENT_ID.WT_EXTRACTOR_SHOT_DEBUFF,
     'wt_impulse_mod_a': FEEDBACK_EVENT_ID.WT_VEHICLE_SILENCE}
    _ABILITIES_SOUNDS = {'wt_impulse_mod_a': {'start': 'ev_white_tiger_stun_effect_start',
                          'stop': 'ev_white_tiger_stun_effect_end'},
     'wt_extractor_shot': {'start': 'ev_white_tiger_stun_effect_imp_start',
                           'stop': 'ev_white_tiger_stun_effect_imp_end'},
     'wt_stun_area_mod_a': {'start': 'ev_white_tiger_stun_effect_start',
                            'stop': 'ev_white_tiger_stun_effect_end'},
     'wt_stun_area': {'start': 'ev_white_tiger_stun_effect_start',
                      'stop': 'ev_white_tiger_stun_effect_end'}}

    def __init__(self):
        super(WTVehicleFactorAppliers, self).__init__()
        self.__guiFeedback = self.entity.guiSessionProvider.shared.feedback
        self.__equipment = None
        if self.equipmentID > 0:
            self.set_equipmentID(self.equipmentID)
            self.__update()
        return

    def onDestroy(self):
        self.__update()
        self.__equipment = None
        super(WTVehicleFactorAppliers, self).onDestroy()
        return

    def set_equipmentID(self, prev):
        if self.equipmentID == prev:
            return
        self.__equipment = vehicles.g_cache.equipments().get(self.equipmentID)

    def set_finishTime(self, prev):
        if self.finishTime == prev:
            return
        self.__update()

    def _onAvatarReady(self):
        if self.equipmentID > 0:
            self.__equipment = vehicles.g_cache.equipments().get(self.equipmentID)
        self.__update()

    def __update(self):
        if self.__equipment is None:
            return
        else:
            duration = self.finishTime - BigWorld.serverTime()
            isShown = duration > 0
            self.__commonUpdate(isShown, duration)
            return

    def __commonUpdate(self, isShown, duration):
        if self.__equipment.name in ('wt_stun_area', 'wt_stun_area_mod_a'):
            self.__updateStunNotificationTimer(isShown, duration)
        if self.__equipment.name == 'wt_stun_area':
            self.__playStunVoiceOver(isShown)
        if self.__equipment.name in self._ABILITIES_MARKERS:
            self.__updateMarker(isShown, duration)
        if self.__equipment.name in self._ABILITIES_NOTIFICATION_TIMER:
            self.__updateNotificationTimer(isShown, duration)
        if self.__equipment.name in self._ABILITIES_SOUNDS:
            self.__playAbilitySound(isShown)

    def __updateMarker(self, isShown, duration):
        self.__guiFeedback.onVehicleFeedbackReceived(self._ABILITIES_MARKERS[self.__equipment.name], self.entity.id, {'isShown': isShown,
         'duration': duration})

    def __updateNotificationTimer(self, isShown, duration):
        timerID, clazz = self._ABILITIES_NOTIFICATION_TIMER[self.__equipment.name]
        value = clazz(isShown, duration, self.finishTime)
        self.entity.guiSessionProvider.invalidateVehicleState(timerID, value, vehicleID=self.entity.id)

    def __updateStunNotificationTimer(self, isShown, duration):
        value = WTTimerViewState(isShown, duration, self.finishTime)
        self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_STUN_AREA, value, vehicleID=self.entity.id)

    def __playAbilitySound(self, isActive):
        if self.entity.id != BigWorld.player().playerVehicleID:
            return
        else:
            ability = self._ABILITIES_SOUNDS.get(self.__equipment.name)
            eventType = 'start' if isActive else 'stop'
            event = ability.get(eventType)
            if event is None:
                return
            SoundGroups.g_instance.playSound2D(event)
            return

    def __playStunVoiceOver(self, isShown):
        vehicleID = avatar_getter.getPlayerVehicleID()
        if isShown and self.entity.health > 0 and vehicleID == self.entity.id:
            playStunAreaHunterVO()
