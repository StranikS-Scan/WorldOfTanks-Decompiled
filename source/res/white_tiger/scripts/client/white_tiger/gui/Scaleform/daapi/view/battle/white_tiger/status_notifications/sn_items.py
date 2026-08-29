# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/status_notifications/sn_items.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_control import avatar_getter
from gui.Scaleform.daapi.view.battle.epic.status_notifications.epic_helpers import getSmokeDataByPredicate
from gui.Scaleform.genConsts.BATTLE_ROYAL_CONSTS import BATTLE_ROYAL_CONSTS
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_TYPES import WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_TYPES

class WhiteTigerOverturnedSN(sn_items.OverturnedSN):

    def _getDescription(self, value=None):
        return backport.text(R.strings.battle_royale.statusNotificationTimers.halfOverturned())


class WhiteTigerHyperionChargingSN(sn_items.DeathZoneDangerSN):

    def _getDescription(self, value=None):
        pass

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_HYPERION_WARNING_CHARGING

    def getViewTypeID(self):
        return WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_HYPERION_WARNING_CHARGING

    def _canBeShown(self, value):
        return value.visible


class WhiteTigerHyperion2025ChargingSN(sn_items.DeathZoneDangerSN):

    def _getDescription(self, value=None):
        pass

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_HYPERION_2025_WARNING_CHARGING

    def getViewTypeID(self):
        return WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_HYPERION_2025_WARNING_CHARGING

    def _canBeShown(self, value):
        return value.visible


class WhiteTigerStunAreaSN(sn_items.TimerSN):

    def _getTitle(self, value):
        return backport.text(R.strings.white_tiger.statusNotificationTimers.stunArea())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_STUN_AREA

    def getViewTypeID(self):
        return WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_STUN_AREA

    def _update(self, value):
        if value.visible:
            self._updateTimeParams(value.totalTime, value.finishTime)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)

    def _getStunType(self):
        pass


class WTTimerViewState(object):
    __slots__ = ('visible', 'totalTime', 'finishTime', 'duration', 'stunType', 'endTime')

    def __init__(self, visible, totalTime, finishTime):
        self.visible = visible
        self.totalTime = totalTime
        self.finishTime = finishTime
        self.duration = finishTime - BigWorld.serverTime()
        self.stunType = 1
        self.endTime = finishTime


class WTExplosiveDamageShieldTimerViewState(WTTimerViewState):
    __slots__ = ('totalInComeDamage', 'maxDamage')

    def __init__(self, visible, totalTime, finishTime, totalInComeDamage, maxDamage):
        super(WTExplosiveDamageShieldTimerViewState, self).__init__(visible, totalTime, finishTime)
        self.totalInComeDamage = totalInComeDamage
        self.maxDamage = maxDamage


class WhiteTigerSilenceSN(sn_items.TimerSN):

    def _getTitle(self, value):
        return backport.text(R.strings.white_tiger.statusNotificationTimers.silence())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_SILENCE

    def getViewTypeID(self):
        return WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_SILENCE

    def _update(self, value):
        if value.visible:
            self._updateTimeParams(value.totalTime, value.finishTime)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)


class WhiteTigerBossInvisibilitySN(sn_items.TimerSN):

    def _getTitle(self, value):
        return backport.text(R.strings.white_tiger.statusNotificationTimers.invisibility())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_BOSS_INVISIBILITY

    def getViewTypeID(self):
        return WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_BOSS_INVISIBILITY

    def _update(self, value):
        if value.visible:
            self._updateTimeParams(value.totalTime, value.finishTime)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)

    def _getStunType(self):
        pass


class WTSmokeSN(sn_items.SmokeSN):

    def _getSmokeData(self, smokesInfo):
        return getSmokeDataByPredicate(smokesInfo, self._isSmokeFitsByTeam, self._postEffectCondition)

    @staticmethod
    def _isSmokeFitsByTeam(teamID):
        return teamID == avatar_getter.getPlayerTeam()

    @staticmethod
    def _postEffectCondition(isPostEffect):
        return not isPostEffect

    @property
    def _stringResource(self):
        return R.strings.white_tiger.statusNotificationTimers


class WTSmokeEnemySN(sn_items.EnemySmokeSN):

    def _getSmokeData(self, smokesInfo):
        return getSmokeDataByPredicate(smokesInfo, self._isSmokeFitsByTeam, self._postEffectCondition)

    @staticmethod
    def _isSmokeFitsByTeam(teamID):
        return teamID != avatar_getter.getPlayerTeam()

    @staticmethod
    def _postEffectCondition(isPostEffect):
        return not isPostEffect

    @property
    def _stringResource(self):
        return R.strings.white_tiger.statusNotificationTimers


class WhiteTigerStunAreaModASN(sn_items.TimerSN):

    def _getTitle(self, value):
        return backport.text(R.strings.white_tiger.statusNotificationTimers.stunAreaModA())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_STUN_AREA_MOD_A

    def getViewTypeID(self):
        return WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_STUN_AREA_MOD_A

    def _update(self, value):
        if value.visible:
            self._updateTimeParams(value.totalTime, value.finishTime)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)

    def _getStunType(self):
        pass


class WhiteTigerExplosiveDamageShieldSN(sn_items.TimerSN):

    def __init__(self, updateCallback):
        super(WhiteTigerExplosiveDamageShieldSN, self).__init__(updateCallback)
        self._vo['additionalState'] = BATTLE_ROYAL_CONSTS.COUNTER_STATE_INITIAL
        self._vo['additionalInfo'] = '+0'

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_ENERGY_SHIELD

    def getViewTypeID(self):
        return WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_ENERGY_SHIELD

    def _update(self, value):
        if value.visible:
            self._updateTimeParams(value.totalTime, value.finishTime)
            self._isVisible = True
            remainDamage = value.maxDamage - value.totalInComeDamage
            remainDamage = remainDamage if remainDamage > 0 else 0
            self._vo['additionalInfo'] = str(remainDamage) + '/' + str(value.maxDamage)
            self._vo['additionalState'] = BATTLE_ROYAL_CONSTS.COUNTER_STATE_EXTRA
            self._sendUpdate()
        else:
            self._setVisible(False)
            self._vo['additionalState'] = BATTLE_ROYAL_CONSTS.COUNTER_STATE_INITIAL

    def _getTitle(self, value):
        return backport.text(R.strings.white_tiger.statusNotificationTimers.ExplosiveDamageShield())


class WhiteTigerDomeSN(sn_items.TimerSN):

    def _getTitle(self, value):
        return backport.text(R.strings.white_tiger.statusNotificationTimers.domeProtectionBuff())

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_DOME

    def getViewTypeID(self):
        return WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_STATIC_SHIELD

    def _update(self, value):
        if value.visible:
            self._updateTimeParams(value.totalTime, value.finishTime)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)

    def _getStunType(self):
        pass


class WhiteTigerAnomalySN(sn_items.DeathZoneDangerSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.WT_ANOMALY

    def getViewTypeID(self):
        return WHITE_TIGER_BATTLE_NOTIFICATIONS_TIMER_TYPES.WT_ANOMALY

    def _canBeShown(self, value):
        return value.visible

    def _getDescription(self, value=None):
        return backport.text(R.strings.ingame_gui.statusNotificationTimers.anomaly())
