# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/markers2d/plugins.py
import BigWorld
import settings
from constants import ROLE_TYPE_TO_LABEL, ROLE_TYPE, INVALID_TIMESTAMP, ARENA_PERIOD
from account_helpers.settings_core.settings_constants import MARKERS
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import SettingsPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import VehicleMarkerPlugin
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import Comp7Keys
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
_COMP7_STATUS_EFFECTS_PRIORITY = (BATTLE_MARKER_STATES.STUN_STATE, BATTLE_MARKER_STATES.COMP7_AOE_HEAL_STATE, BATTLE_MARKER_STATES.COMP7_AOE_INSPIRE_STATE)

class Comp7SettingsPlugin(SettingsPlugin):
    __BEFORE_BATTLE_OVERRIDES = {MARKERS.ALLY: (('markerAltIcon', False),
                    ('markerAltLevel', False),
                    ('markerAltHpIndicator', False),
                    ('markerAltDamage', False),
                    ('markerAltHp', 3),
                    ('markerAltVehicleName', True),
                    ('markerAltPlayerName', True),
                    ('markerAltAimMarker2D', False))}
    __ADDITIONAL_SETTINGS = {name:(('markerAltRoleName', 1), ('markerAltRoleSkillLevel', 1)) for name in MARKERS.ALL()}

    def __init__(self, parentObj):
        super(Comp7SettingsPlugin, self).__init__(parentObj)
        self._overrides = {}
        self._additionalSettings = self.__ADDITIONAL_SETTINGS

    def start(self, *args):
        super(Comp7SettingsPlugin, self).start(*args)
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        arenaPeriod = periodCtrl.getPeriod() if periodCtrl else None
        if arenaPeriod:
            self.__onArenaPeriodChange(arenaPeriod)
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
        return

    def stop(self):
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        super(Comp7SettingsPlugin, self).stop()
        return

    def __onArenaPeriodChange(self, period, *_, **__):
        self._overrides = self.__BEFORE_BATTLE_OVERRIDES if period < ARENA_PERIOD.BATTLE else {}
        self._setMarkerSettings(notify=True)


class Comp7VehicleMarkerPlugin(VehicleMarkerPlugin):
    __slots__ = ()

    def start(self):
        super(Comp7VehicleMarkerPlugin, self).start()
        prebattleCtrl = self.sessionProvider.dynamic.comp7PrebattleSetup
        if prebattleCtrl is not None:
            prebattleCtrl.onTeammateSelectionStatuses += self.__onTeammateSelectionStatuses
            prebattleCtrl.onBattleStarted += self.__onBattleStarted
        return

    def stop(self):
        prebattleCtrl = self.sessionProvider.dynamic.comp7PrebattleSetup
        if prebattleCtrl is not None:
            prebattleCtrl.onTeammateSelectionStatuses -= self.__onTeammateSelectionStatuses
            prebattleCtrl.onBattleStarted -= self.__onBattleStarted
        super(Comp7VehicleMarkerPlugin, self).stop()
        return

    def invalidateVehicleStatus(self, flags, vInfo, arenaDP):
        marker = self._markers.get(vInfo.vehicleID)
        if marker is not None:
            self.__setIsPlayerLoaded(marker, vInfo)
        return

    def updateVehiclesInfo(self, updated, arenaDP):
        super(Comp7VehicleMarkerPlugin, self).updateVehiclesInfo(updated, arenaDP)
        for _, vInfo in updated:
            vehicleID = vInfo.vehicleID
            if vehicleID not in self._markers:
                continue
            marker = self._markers[vehicleID]
            self.__setModeSpecificData(marker, vInfo)

    def _getMarkerSymbol(self, _):
        return settings.Comp7markersSymbolsNames.COMP7_VEHICLE_MARKER

    def _setMarkerInitialState(self, marker, vInfo):
        super(Comp7VehicleMarkerPlugin, self)._setMarkerInitialState(marker, vInfo)
        self.__setModeSpecificData(marker, vInfo)

    def _onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        super(Comp7VehicleMarkerPlugin, self)._onVehicleFeedbackReceived(eventID, vehicleID, value)
        arenaDP = self.sessionProvider.getArenaDP()
        if arenaDP is None or vehicleID not in self._markers:
            return
        else:
            marker = self._markers[vehicleID]
            vInfo = arenaDP.getVehicleInfo(vehicleID)
            handle = marker.getMarkerID()
            if eventID == FEEDBACK_EVENT_ID.VEHICLE_AOE_HEAL:
                self.__updateAoeHealMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_AOE_INSPIRE:
                self.__updateAoeInspireMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_RISKY_ATTACK_BUFF:
                self.__updateRiskyAttackBuffMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_RISKY_ATTACK_HEAL:
                self.__updateRiskyAttackHealMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_BERSERK:
                self.__updateBerserkMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_ALLY_SUPPORT:
                self.__updateAllySupportMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_HUNTER:
                self.__updateHunterMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_FAST_RECHARGE:
                self.__updateFastRechargeMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_JUGGERNAUT:
                self.__updateJuggernautMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_SURE_SHOT:
                self.__updateSureShotMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_CONCENTRATION:
                self.__updateConcentrationMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_SNIPER:
                self.__updateSniperMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_MARCH:
                self.__updateMarchMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_AGGRESSIVE_DETECTION:
                self.__updateAggressiveDetectionMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_POINT_RECON:
                self.__updatePointReconMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_RED_LINE:
                self.__updateRedLineMarker(vehicleID, handle, value)
            elif eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD:
                self.__setRoleSkillLevel(marker, vInfo)
            return

    def _getMarkerStatusPriority(self, markerState):
        aoeMarker = markerState.statusID in (BATTLE_MARKER_STATES.COMP7_AOE_INSPIRE_STATE, BATTLE_MARKER_STATES.COMP7_AOE_HEAL_STATE)
        if aoeMarker and markerState.isSourceVehicle:
            return -2
        try:
            return _COMP7_STATUS_EFFECTS_PRIORITY.index(markerState.statusID)
        except ValueError:
            return -1

    def _setupHealth(self, marker, vInfo):
        validHealth = self.__validatePrebattleHealth(vInfo.vehicleID, marker.getHealth())
        self._invokeMarker(marker.getMarkerID(), 'setHealth', validHealth)

    def _updateVehicleHealth(self, vehicleID, handle, newHealth, aInfo, attackReasonID):
        validHealth = self.__validatePrebattleHealth(vehicleID, newHealth)
        super(Comp7VehicleMarkerPlugin, self)._updateVehicleHealth(vehicleID, handle, validHealth, aInfo, attackReasonID)

    def __setModeSpecificData(self, marker, vInfo):
        self.__setRole(marker, vInfo)
        self.__setRoleSkillLevel(marker, vInfo)
        self.__setIsPlayerLoaded(marker, vInfo)
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        if periodCtrl is not None and periodCtrl.getPeriod() < ARENA_PERIOD.BATTLE:
            vehSwitchComponent = avatar_getter.getArena().teamInfo.TeamInfoInBattleVehicleSwitch
            if vehSwitchComponent is not None:
                vehStatus = vehSwitchComponent.statuses.get(vInfo.vehicleID, False)
                self.__onTeammateSelectionStatuses({vInfo.vehicleID: vehStatus})
        return

    def __setRole(self, marker, vInfo):
        role = vInfo.vehicleType.role
        roleName = ROLE_TYPE_TO_LABEL[role] if role != ROLE_TYPE.NOT_DEFINED else None
        self._invokeMarker(marker.getMarkerID(), 'setRoleName', roleName)
        return

    def __setRoleSkillLevel(self, marker, vInfo):
        if not marker.getIsPlayerTeam():
            return
        if marker.isAlive():
            roleSkillLevel = vInfo.gameModeSpecific.getValue(Comp7Keys.ROLE_SKILL_LEVEL, default=0)
        else:
            roleSkillLevel = 0
        self._invokeMarker(marker.getMarkerID(), 'setRoleSkillLevel', roleSkillLevel)

    def __setIsPlayerLoaded(self, marker, vInfo):
        self._invokeMarker(marker.getMarkerID(), 'setIsPlayerLoaded', vInfo.isReady())

    def __updateAoeHealMarker(self, vehicleID, handle, state):
        showCountdown = state.get('isSourceVehicle', False)
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_AOE_HEAL_STATE, showCountdown=showCountdown)

    def __updateAoeInspireMarker(self, vehicleID, handle, state):
        showCountdown = state.get('isSourceVehicle', False)
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_AOE_INSPIRE_STATE, showCountdown=showCountdown)

    def __updateBerserkMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_BERSERK_STATE)

    def __updateAllySupportMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_ALLY_SUPPORT_STATE)

    def __updateHunterMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_HUNTER_STATE)

    def __updateRiskyAttackBuffMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_RISKY_ATTACK_STATE)

    def __updateRiskyAttackHealMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_RISKY_ATTACK_HEAL_STATE)

    def __updateFastRechargeMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_FAST_RECHARGE_STATE)

    def __updateJuggernautMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_JUGGERNAUT_STATE)

    def __updateSureShotMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_SURE_SHOT_STATE)

    def __updateConcentrationMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_CONCENTRATION_STATE)

    def __updateSniperMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_SNIPER_STATE)

    def __updateMarchMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_MARCH_STATE)

    def __updateAggressiveDetectionMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_AGGRESSIVE_DETECTION_STATE)

    def __updatePointReconMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_POINT_RECON_STATE)

    def __updateRedLineMarker(self, vehicleID, handle, state):
        self.__updateAbilityMarker(vehicleID, state, handle, BATTLE_MARKER_STATES.COMP7_ARTYLLERY_SUPPORT_STATE)

    def __updateAbilityMarker(self, vehicleID, state, handle, stateID, showCountdown=False):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None or not vehicle.isAlive():
            return
        else:
            show = not state.get('finishing', False)
            isSourceVehicle = state.get('isSourceVehicle', False)
            endTime = state.get('endTime', INVALID_TIMESTAMP)
            duration = max(endTime - BigWorld.serverTime(), 0) if show and endTime != INVALID_TIMESTAMP else 0
            self._updateMarkerTimer(vehicleID, handle=handle, duration=duration, statusID=stateID, showCountdown=showCountdown, isSourceVehicle=isSourceVehicle)
            return

    def __validatePrebattleHealth(self, vehicleID, newHealth):
        arena = avatar_getter.getArena()
        if arena.period >= ARENA_PERIOD.BATTLE:
            return newHealth
        else:
            arenaDP = self.sessionProvider.getArenaDP()
            if arenaDP is None:
                return newHealth
            vehSwitchComponent = avatar_getter.getArena().teamInfo.TeamInfoInBattleVehicleSwitch
            return newHealth if vehSwitchComponent is None or vehSwitchComponent.checkVehicleConfirmation(vehicleID) else arenaDP.getVehicleInfo(vehicleID).vehicleType.maxHealth

    def __onTeammateSelectionStatuses(self, statuses):
        for vehicleID, status in statuses.iteritems():
            marker = self._markers.get(vehicleID)
            if marker is not None:
                value = 'positive' if status else ''
                self._invokeMarker(self._markers[vehicleID].getMarkerID(), 'changeObjectiveActionMarker', value)

        return

    def __onBattleStarted(self):
        statuses = {vehicleID:False for vehicleID in self._markers.iterkeys()}
        self.__onTeammateSelectionStatuses(statuses)
