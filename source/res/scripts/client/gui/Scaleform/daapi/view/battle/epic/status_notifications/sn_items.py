# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/status_notifications/sn_items.py
import typing
from constants import VEHICLE_MISC_STATUS
from gui.Scaleform.daapi.view.battle.epic.status_notifications.epic_helpers import getSmokeDataByPredicate, getEquipmentById
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, PROGRESS_CIRCLE_TYPE
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.battle_constants import DestroyTimerViewState

class _EpicLocalizationProvider(sn_items.LocalizationProvider):

    @property
    def _stringResource(self):
        return R.strings.epic_battle.statusNotificationTimers


class _EpicSmokeMixin(object):

    @staticmethod
    def _isSmokeFitsByTeam(teamID):
        raise NotImplementedError

    @staticmethod
    def _postEffectCondition(isPostEffect):
        raise NotImplementedError


class EpicDeathZoneDamagingSN(_EpicLocalizationProvider, sn_items.DeathZoneDamagingSN):
    pass


class EpicDeathZoneDangerSN(_EpicLocalizationProvider, sn_items.DeathZoneDangerSN):
    pass


class EpicDeathZoneWarningSN(_EpicLocalizationProvider, sn_items.DeathZoneWarningSN):
    pass


class EpicHealingSN(_EpicLocalizationProvider, sn_items.HealingSN):
    pass


class EpicHealingCooldownSN(_EpicLocalizationProvider, sn_items.HealingCooldownSN):
    pass


class EpicRepairingSN(_EpicLocalizationProvider, sn_items.RepairingSN):
    pass


class EpicRepairingCooldownSN(_EpicLocalizationProvider, sn_items.RepairingCooldownSN):
    pass


class EpicInspireSN(_EpicLocalizationProvider, sn_items.InspireSN):

    def _getIsPulseVisible(self):
        return True


class EpicInspireCooldownSN(_EpicLocalizationProvider, sn_items.InspireCooldownSN):
    pass


class EpicInspireSourceSN(_EpicLocalizationProvider, sn_items.InspireSourceSN):

    def _getIsPulseVisible(self):
        return True


class EpicInspireInactivationSourceSN(_EpicLocalizationProvider, sn_items.InspireInactivationSourceSN):
    pass


class EpicSmokeSN(_EpicLocalizationProvider, _EpicSmokeMixin, sn_items.SmokeSN):

    def _getSmokeData(self, smokesInfo):
        return getSmokeDataByPredicate(smokesInfo, self._isSmokeFitsByTeam, self._postEffectCondition)

    @staticmethod
    def _isSmokeFitsByTeam(teamID):
        return teamID == avatar_getter.getPlayerTeam()

    @staticmethod
    def _postEffectCondition(isPostEffect):
        return not isPostEffect


class EpicEnemySmokeSN(_EpicLocalizationProvider, _EpicSmokeMixin, sn_items.EnemySmokeSN):

    def _getSmokeData(self, smokesInfo):
        return getSmokeDataByPredicate(smokesInfo, self._isSmokeFitsByTeam, self._postEffectCondition)

    @staticmethod
    def _isSmokeFitsByTeam(teamID):
        return teamID != avatar_getter.getPlayerTeam()

    @staticmethod
    def _postEffectCondition(isPostEffect):
        return not isPostEffect


class EpicEnemySmokePostEffectSN(_EpicLocalizationProvider, _EpicSmokeMixin, sn_items.EnemySmokeSN):

    def _getSmokeData(self, smokesInfo):
        return getSmokeDataByPredicate(smokesInfo, self._isSmokeFitsByTeam, self._postEffectCondition)

    def _getTitle(self, value):
        return backport.text(self._stringResource.smoke.enemyPostEffect())

    @staticmethod
    def _isSmokeFitsByTeam(teamID):
        return teamID != avatar_getter.getPlayerTeam()

    @staticmethod
    def _postEffectCondition(isPostEffect):
        return isPostEffect


class CaptureBlockSN(_EpicLocalizationProvider, sn_items.TimerSN):

    def __init__(self, updateCallback):
        super(CaptureBlockSN, self).__init__(updateCallback)
        self.__isBlocked = False

    def start(self):
        super(CaptureBlockSN, self).start()
        self._subscribeOnVehControlling()
        ctrl = self._sessionProvider.dynamic.progressTimer
        if ctrl is not None:
            ctrl.onVehicleLeft += self.__onVehicleLeft
            ctrl.onVehicleEntered += self.__onVehicleEntered
        return

    def destroy(self):
        ctrl = self._sessionProvider.dynamic.progressTimer
        if ctrl is not None:
            ctrl.onVehicleEntered -= self.__onVehicleEntered
            ctrl.onVehicleLeft -= self.__onVehicleLeft
        super(CaptureBlockSN, self).destroy()
        return

    def getItemID(self):
        return VEHICLE_VIEW_STATE.CAPTURE_BLOCKED

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.CAPTURE_BLOCK

    def _update(self, duration):
        if duration:
            self._updateTimeParams(duration, 0)
            self._isVisible = True
            self.__isBlocked = False
            self._sendUpdate()
        else:
            self.__isBlocked = False
            self._setVisible(False)

    def _getTitle(self, value):
        return backport.text(self._stringResource.captureBlock.blocked())

    def __onVehicleLeft(self, *_):
        if self.__isBlocked:
            self._setVisible(False)

    def __onVehicleEntered(self, *_):
        if self.__isBlocked:
            self._setVisible(True)


class ResupplyTimerSN(sn_items.TimerSN):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, updateCallback):
        super(ResupplyTimerSN, self).__init__(updateCallback)
        self.__curPointIdx = -1

    def start(self):
        super(ResupplyTimerSN, self).start()
        ctrl = self._sessionProvider.dynamic.progressTimer
        if ctrl:
            ctrl.onTimerUpdated += self.__onTimerUpdated
            ctrl.onVehicleEntered += self.__onVehicleEntered
            ctrl.onVehicleLeft += self.__onVehicleLeft
            ctrl.onCircleStatusChanged += self.__onCircleStatusChanged
            ctrl.onProgressUpdate += self.__onProgressUpdate

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.RESUPPLY

    def getItemID(self):
        return VEHICLE_VIEW_STATE.PROGRESS_CIRCLE

    def destroy(self):
        super(ResupplyTimerSN, self).destroy()
        ctrl = self._sessionProvider.dynamic.progressTimer
        if ctrl:
            ctrl.onTimerUpdated -= self.__onTimerUpdated
            ctrl.onVehicleEntered -= self.__onVehicleEntered
            ctrl.onVehicleLeft -= self.__onVehicleLeft
            ctrl.onCircleStatusChanged -= self.__onCircleStatusChanged
            ctrl.onProgressUpdate -= self.__onProgressUpdate
        self.__curPointIdx = -1

    def _update(self, value):
        circleType, isVisible = value
        if circleType is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        self._setVisible(isVisible)

    def __onVehicleEntered(self, circleType, pointIdx, state):
        if circleType is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        self.__curPointIdx = pointIdx
        self.__updateAdditionalState(state)

    def __onVehicleLeft(self, circleType, _):
        if circleType is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        self.__curPointIdx = -1

    def __onCircleStatusChanged(self, circleType, pointIdx, state):
        if circleType is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        if self.__curPointIdx != pointIdx:
            return
        if state == EPIC_CONSTS.RESUPPLY_FULL:
            self._updateTimeParams(0, 0)
        elif state == EPIC_CONSTS.RESUPPLY_BLOCKED:
            self._updateTimeParams(0, 0)
        self.__updateAdditionalState(state)

    def __updateAdditionalState(self, state):
        if 'additionalState' in self._vo and self._vo['additionalState'] == state:
            return
        self._vo['additionalState'] = state
        if self._isVisible:
            self._sendUpdate()

    def __onTimerUpdated(self, circleType, pointIdx, timeLeft):
        if circleType is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        if pointIdx != self.__curPointIdx:
            return
        self._updateTimeParams(timeLeft, 0)
        if self._isVisible:
            self._sendUpdate()

    def __onProgressUpdate(self, circleType, _, value):
        if circleType is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        valueStr = str(value)
        if 'additionalInfo' in self._vo and self._vo['additionalInfo'] == valueStr:
            return
        self._vo['additionalInfo'] = valueStr
        if self._isVisible:
            self._sendUpdate()


class RecoverySN(sn_items.DestroyMiscTimerSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.RECOVERY

    def getItemID(self):
        return VEHICLE_VIEW_STATE.RECOVERY

    def _getSupportedLevel(self):
        return self._ANY_SUPPORTED_LEVEL

    def _getSupportedMiscStatus(self):
        return VEHICLE_VIEW_STATE.RECOVERY

    def _update(self, value):
        isRecovery, totalTime, _ = value
        if not isRecovery:
            self._setVisible(False)
        else:
            self._isVisible = True
            self._updateTimeParams(totalTime, 0)
            self._sendUpdate()


class SectorAirstrikeSN(sn_items.DestroyMiscTimerSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.SECTOR_AIRSTRIKE

    def _getSupportedLevel(self):
        return self._ANY_SUPPORTED_LEVEL

    def _getSupportedMiscStatus(self):
        return VEHICLE_MISC_STATUS.IN_DEATH_ZONE


class _StealthBaseSN(_EpicLocalizationProvider, sn_items.BuffSN):

    def start(self):
        super(_StealthBaseSN, self).start()
        self._subscribeOnVehControlling()

    def _updateTimeValues(self, value):
        self._updateTimeParams(value.duration, value.endTime)

    def _isValidForUpdateVisibility(self, value):
        return value.duration > 0.0 and value.isActive == self._getInActivationState()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.STEALTH_RADAR


class StealthSN(_StealthBaseSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.STEALTH_RADAR

    def _getTitle(self, value):
        return backport.text(self._stringResource.stealthRadar.active())

    def _getInActivationState(self):
        return True


class StealthInactiveSN(_StealthBaseSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.STEALTH_RADAR_INACTIVE

    def _getTitle(self, value):
        equipment = getEquipmentById(value['equipmentID'])
        return backport.text(self._stringResource.stealthRadar.inactive(), activationDelay=int(equipment.inactivationDelay))

    def _getInActivationState(self):
        return False
