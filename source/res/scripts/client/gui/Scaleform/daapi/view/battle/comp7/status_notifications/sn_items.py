# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/status_notifications/sn_items.py
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TIMER_TYPES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R

class _Comp7LocalizationProvider(sn_items.LocalizationProvider):

    @property
    def _stringResource(self):
        return R.strings.comp7.battlePage.statusNotificationTimers


class Comp7HealingSN(_Comp7LocalizationProvider, sn_items.HealingSN):
    pass


class _Comp7BuffSN(_Comp7LocalizationProvider, sn_items.TimerSN):
    _ITEM_ID = None
    _VIEW_TYPE_ID = None

    def __init__(self, updateCallback):
        super(_Comp7BuffSN, self).__init__(updateCallback)
        self._isSourceVehicle = False

    def start(self):
        super(_Comp7BuffSN, self).start()
        self._subscribeOnVehControlling()

    def getItemID(self):
        return self._ITEM_ID

    def getViewTypeID(self):
        return self._VIEW_TYPE_ID

    def isSourceVehicle(self):
        return self._isSourceVehicle

    def _update(self, stateInfo):
        self._isVisible = not stateInfo.get('finishing', False)
        self._isSourceVehicle = stateInfo.get('isSourceVehicle', False)
        if self._isVisible:
            self._updateTimeParams(stateInfo.get('duration'), stateInfo.get('endTime'))
        self._sendUpdate()


class _Comp7PulseVisibleSourceRelatedBuffSN(_Comp7BuffSN):

    def _update(self, stateInfo):
        self._isPulseVisible = not stateInfo.get('isSourceVehicle', False)
        super(_Comp7PulseVisibleSourceRelatedBuffSN, self)._update(stateInfo)


class AoeHealSN(_Comp7PulseVisibleSourceRelatedBuffSN):
    _ITEM_ID = VEHICLE_VIEW_STATE.AOE_HEAL
    _VIEW_TYPE_ID = _TIMER_TYPES.COMP7_AOE_HEAL

    def _getTitle(self, value):
        isSourceVehicle = value.get('isSourceVehicle', False)
        res = self._stringResource.aoeHeal
        return backport.text(res.healing() if isSourceVehicle else res.healed())


class AoeInspireSN(_Comp7PulseVisibleSourceRelatedBuffSN):
    _ITEM_ID = VEHICLE_VIEW_STATE.AOE_INSPIRE
    _VIEW_TYPE_ID = _TIMER_TYPES.COMP7_AOE_INSPIRE

    def _getTitle(self, value):
        isSourceVehicle = value.get('isSourceVehicle', False)
        res = self._stringResource.aoeInspire
        return backport.text(res.inspiring() if isSourceVehicle else res.inspired())


class RiskyAttackBuffSN(_Comp7BuffSN):
    _ITEM_ID = VEHICLE_VIEW_STATE.RISKY_ATTACK_BUFF
    _VIEW_TYPE_ID = _TIMER_TYPES.COMP7_RISKY_ATTACK

    def _getTitle(self, value):
        return backport.text(self._stringResource.riskyAttack.buff())


class RiskyAttackHealSN(_Comp7BuffSN):
    _ITEM_ID = VEHICLE_VIEW_STATE.RISKY_ATTACK_HEAL
    _VIEW_TYPE_ID = _TIMER_TYPES.COMP7_RISKY_ATTACK_HEAL

    def _getTitle(self, value):
        return backport.text(self._stringResource.riskyAttack.heal())


class BerserkSN(_Comp7BuffSN):
    _ITEM_ID = VEHICLE_VIEW_STATE.BERSERK
    _VIEW_TYPE_ID = _TIMER_TYPES.COMP7_BERSERK

    def _getTitle(self, value):
        return backport.text(self._stringResource.berserk())


class SniperSN(_Comp7BuffSN):
    _ITEM_ID = VEHICLE_VIEW_STATE.SNIPER
    _VIEW_TYPE_ID = _TIMER_TYPES.COMP7_SNIPER

    def _getTitle(self, value):
        return backport.text(self._stringResource.sniper())


class AllySupportSN(_Comp7BuffSN):
    _ITEM_ID = VEHICLE_VIEW_STATE.ALLY_SUPPORT
    _VIEW_TYPE_ID = _TIMER_TYPES.COMP7_ALLY_SUPPORT

    def _getTitle(self, value):
        return backport.text(self._stringResource.allySupport())


class HunterSN(_Comp7BuffSN):
    _ITEM_ID = VEHICLE_VIEW_STATE.HUNTER
    _VIEW_TYPE_ID = _TIMER_TYPES.COMP7_HUNTER

    def _getTitle(self, value):
        return backport.text(self._stringResource.hunter())


class JuggernautSN(_Comp7BuffSN):
    _ITEM_ID = VEHICLE_VIEW_STATE.JUGGERNAUT
    _VIEW_TYPE_ID = _TIMER_TYPES.COMP7_JUGGERNAUT

    def _getTitle(self, value):
        return backport.text(self._stringResource.juggernaut())


class SureShotSN(_Comp7BuffSN):
    _ITEM_ID = VEHICLE_VIEW_STATE.SURE_SHOT
    _VIEW_TYPE_ID = _TIMER_TYPES.COMP7_SURE_SHOT

    def _getTitle(self, value):
        return backport.text(self._stringResource.sureShot())


class ConcentrationSN(_Comp7BuffSN):
    _ITEM_ID = VEHICLE_VIEW_STATE.CONCENTRATION
    _VIEW_TYPE_ID = _TIMER_TYPES.COMP7_CONCENTRATION

    def _getTitle(self, value):
        return backport.text(self._stringResource.concentration())


class MarchSN(_Comp7BuffSN):
    _ITEM_ID = VEHICLE_VIEW_STATE.MARCH
    _VIEW_TYPE_ID = _TIMER_TYPES.COMP7_MARCH

    def _getTitle(self, value):
        return backport.text(self._stringResource.march())


class AggressiveDetectionSN(_Comp7BuffSN):
    _ITEM_ID = VEHICLE_VIEW_STATE.AGGRESSIVE_DETECTION
    _VIEW_TYPE_ID = _TIMER_TYPES.COMP7_AGGRESSIVE_DETECTION

    def _getTitle(self, value):
        return backport.text(self._stringResource.aggressiveDetection())
