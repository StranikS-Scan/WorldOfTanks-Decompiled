# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/tooltips/efficiency_tooltips.py
import typing
from constants import DEATH_REASON_ALIVE
from frameworks.wulf.view.array import fillResourcesArray
from gui.battle_results.pbs_helpers.common import getEnemies
from gui.battle_results.presenters.packers.interfaces import ITooltipPacker
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.critical_damage_group_model import CriticalDamageGroupModel
from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.critical_damage_tooltip_model import CriticalDamageTooltipModel
from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.efficiency_item_model import Unit, EfficiencyItemModel
from soft_exception import SoftException
from gui.impl.gen.view_models.views.lobby.battle_results.efficiency_param_constants import EfficiencyParamConstants
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.battle_results.reusable import _ReusableInfo
    from gui.battle_results.reusable.shared import VehicleSummarizeInfo
    from gui.impl.gen_utils import DynAccessor
    from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.efficiency_tooltip_model import EfficiencyTooltipModel
_STR_PATH = R.strings.battle_results.common
_IMG_PATH = R.images.gui.maps.icons.library.efficiency.statsParameters

def getEnemyInfo(userName, reusable, results):
    for enemy in getEnemies(reusable, results):
        if enemy.player.realName == userName:
            return enemy


def getPlayerResults(battleResults, userName):
    reusable, results = battleResults.reusable, battleResults.results
    if userName is not None:
        playerResults = getEnemyInfo(userName, reusable, results)
    else:
        playerResults = reusable.getPersonalVehiclesInfo(results['personal'])
    return playerResults


def getStunValues(playerResult, isZeroValuesVisible=False):
    assisted = playerResult.damageAssistedStun
    count = playerResult.stunNum
    duration = playerResult.stunDuration
    return (assisted, count, duration) if isZeroValuesVisible or count > 0 or assisted > 0 or duration > 0 else None


def getDamageValues(playerResult, isZeroValuesVisible=False):
    piercings = playerResult.piercings
    damageDealt = playerResult.damageDealt
    return (damageDealt, piercings) if isZeroValuesVisible or damageDealt > 0 else None


def getArmorValues(playerResult, isZeroValuesVisible=False):
    noDamage = playerResult.noDamageDirectHitsReceived
    damageBlocked = playerResult.damageBlockedByArmor
    if isZeroValuesVisible or noDamage > 0 or damageBlocked > 0:
        rickochets = playerResult.rickochetsReceived
        return (rickochets, noDamage, damageBlocked)
    else:
        return None


def getAssistValues(playerResult, isZeroValuesVisible=False):
    damageAssistedTrack = playerResult.damageAssistedTrack
    damageAssistedRadio = playerResult.damageAssistedRadio
    total = damageAssistedTrack + damageAssistedRadio
    return (damageAssistedRadio, damageAssistedTrack, total) if isZeroValuesVisible or total > 0 else None


def getKilledReasons(reusable, results, userName, isZeroValuesVisible=False):
    if userName:
        reason = [ enemy.deathReason for enemy in getEnemies(reusable, results) if enemy.player.realName == userName and enemy.targetKills and enemy.deathReason >= DEATH_REASON_ALIVE ]
        return reason
    else:
        allReasons = [ enemy.deathReason for enemy in getEnemies(reusable, results) if enemy.targetKills and enemy.deathReason >= DEATH_REASON_ALIVE ]
        return allReasons if isZeroValuesVisible and len(allReasons) == 1 else None


def getCapturePointsValues(playerResult):
    return (playerResult.capturePoints,) if playerResult.capturePoints > 0 else None


def getDefencePointsValues(playerResult):
    return (playerResult.droppedCapturePoints,) if playerResult.droppedCapturePoints > 0 else None


class BaseParameter(object):
    _UNITS_TO_RESOURCE_IDS_MAP = {Unit.COUNT: _STR_PATH.tooltip.params.val,
     Unit.SEC: _STR_PATH.tooltip.params.val.seconds}
    _TITLE = None
    _DESCRIPTION = None
    _ICON = None
    _ITEM_LABELS = ()
    _STATUS = None

    @classmethod
    def getTitle(cls):
        return cls._TITLE

    @classmethod
    def getIcon(cls):
        return cls._ICON

    @classmethod
    def getDescription(cls):
        return cls._DESCRIPTION

    @classmethod
    def getLables(cls):
        return [ (item[0], cls._UNITS_TO_RESOURCE_IDS_MAP.get(item[1], R.invalid)) for item in cls._ITEM_LABELS ]

    @classmethod
    def getValues(cls, *args):
        return None

    @classmethod
    def getStatuses(cls, *args):
        return None


class SpottedParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.spotted.header
    _DESCRIPTION = _STR_PATH.tooltip.spotted.description
    _ICON = _IMG_PATH.spotted


class CapturePointsParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.capture.header
    _DESCRIPTION = _STR_PATH.tooltip.capture.description
    _ICON = _IMG_PATH.capturePoints
    _ITEM_LABELS = ((_STR_PATH.tooltip.capture.totalPoints, None),)

    @classmethod
    def getValues(cls, playerResult, isAdditionalValuesVisible, _):
        return None if not isAdditionalValuesVisible else getCapturePointsValues(playerResult)


class DefencePointsParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.defence.header
    _DESCRIPTION = _STR_PATH.tooltip.defence.description
    _ICON = _IMG_PATH.droppedCapturePoints
    _ITEM_LABELS = ((_STR_PATH.tooltip.defence.totalPoints, None),)

    @classmethod
    def getValues(cls, playerResult, isAdditionalValuesVisible, _):
        return None if not isAdditionalValuesVisible else getDefencePointsValues(playerResult)


class KillsParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.kill.header
    _DESCRIPTION = _STR_PATH.tooltip.killCommon.description
    _ICON = _IMG_PATH.kills
    _STATUS = _STR_PATH.tooltip

    @classmethod
    def getStatuses(cls, reusable, results, userName, isZeroValuesVisible=False):
        reasons = getKilledReasons(reusable, results, userName, isZeroValuesVisible)
        if not reasons:
            return None
        else:
            statuses = []
            for deathReason in reasons:
                killStatus = cls._STATUS.dyn('kill{}'.format(deathReason))
                if killStatus != R.invalid():
                    statuses.append(killStatus.description())

            return statuses


class DamageDealtParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.damage.header
    _DESCRIPTION = _STR_PATH.tooltip.damage.description
    _ICON = _IMG_PATH.damageDealt
    _ITEM_LABELS = ((_STR_PATH.totalTooltip.damage.part1, Unit.COUNT), (_STR_PATH.totalTooltip.damage.part2, None))

    @classmethod
    def getValues(cls, playerResult, _, isZeroValuesVisible=False):
        return getDamageValues(playerResult, isZeroValuesVisible)


class StunParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.stun.header
    _DESCRIPTION = _STR_PATH.tooltip.stun.description
    _ICON = _IMG_PATH.damageAssistedStun
    _ITEM_LABELS = ((_STR_PATH.totalTooltip.stun.part1, Unit.COUNT), (_STR_PATH.totalTooltip.stun.part2, None), (_STR_PATH.totalTooltip.stun.part3, Unit.SEC))

    @classmethod
    def getValues(cls, playerResult, _, isZeroValuesVisible=False):
        return getStunValues(playerResult, isZeroValuesVisible)


class DamageAssistedParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.assist.header
    _DESCRIPTION = _STR_PATH.tooltip.assist.description
    _ICON = _IMG_PATH.damageAssisted
    _ITEM_LABELS = ((_STR_PATH.totalTooltip.assist.part1, Unit.COUNT), (_STR_PATH.totalTooltip.assist.part2, Unit.COUNT), (_STR_PATH.totalTooltip.assist.total, Unit.COUNT))

    @classmethod
    def getValues(cls, playerResult, _, isZeroValuesVisible=False):
        return getAssistValues(playerResult, isZeroValuesVisible)


class DamageBlockedByArmorParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.armor.header
    _DESCRIPTION = _STR_PATH.tooltip.armor.description
    _ICON = _IMG_PATH.damageBlockedByArmor
    _ITEM_LABELS = ((_STR_PATH.totalTooltip.armor.part1, None), (_STR_PATH.totalTooltip.armor.part2, None), (_STR_PATH.totalTooltip.armor.part3, Unit.COUNT))

    @classmethod
    def getValues(cls, playerResult, _, isZeroValuesVisible=False):
        return getArmorValues(playerResult, isZeroValuesVisible)


PARAMETERS_TO_TOOLTIP_MAP = {EfficiencyParamConstants.STUN: StunParameter,
 EfficiencyParamConstants.DAMAGE_DEALT: DamageDealtParameter,
 EfficiencyParamConstants.DAMAGE_BLOCKED_BY_ARMOR: DamageBlockedByArmorParameter,
 EfficiencyParamConstants.DAMAGE_ASSISTED: DamageAssistedParameter,
 EfficiencyParamConstants.SPOTTED: SpottedParameter,
 EfficiencyParamConstants.KILLS: KillsParameter,
 EfficiencyParamConstants.CAPTURE_POINTS: CapturePointsParameter,
 EfficiencyParamConstants.DROPPED_CAPTURE_POINTS: DefencePointsParameter}

class EfficiencyTooltipsPacker(ITooltipPacker):
    __slots__ = ()
    _TOOLTIPS = PARAMETERS_TO_TOOLTIP_MAP

    @classmethod
    def packTooltip(cls, model, battleResults, ctx=None):
        if not ctx['paramType']:
            raise SoftException('Missing parameter type for the EfficiencyTooltip')
        paramType = ctx['paramType']
        isZeroValuesVisible = ctx.get('isZeroValuesVisible', False)
        isAdditionalValuesVisible = ctx.get('isAdditionalValuesVisible', False)
        userName = ctx.get('userName')
        playerResults = getPlayerResults(battleResults, userName)
        reusable, results = battleResults.reusable, battleResults.results
        parameter = cls._getEfficiencyParameter(paramType)
        tooltipHelper = cls._TOOLTIPS.get(parameter)
        if tooltipHelper is not None:
            model.setTitle(tooltipHelper.getTitle()())
            model.setDescription(tooltipHelper.getDescription()())
            model.setIcon(tooltipHelper.getIcon()())
            values = tooltipHelper.getValues(playerResults, isAdditionalValuesVisible, isZeroValuesVisible)
            if values is not None:
                cls.__packDetails(model.getDetails(), values, tooltipHelper.getLables())
            statuses = tooltipHelper.getStatuses(reusable, results, userName, isZeroValuesVisible)
            if statuses is not None:
                fillResourcesArray(statuses, model.getStatuses())
        return

    @staticmethod
    def _getEfficiencyParameter(paramType):
        return paramType

    @staticmethod
    def __packDetails(detailsModel, values, labels):
        detailsModel.clear()
        for value, (label, valueType) in zip(values, labels):
            item = EfficiencyItemModel()
            item.setValue(value)
            item.setLabel(label())
            item.setValueType(valueType())
            detailsModel.addViewModel(item)

        detailsModel.invalidate()


class CriticalDamageTooltipPacker(ITooltipPacker):

    @classmethod
    def packTooltip(cls, model, battleResults, ctx=None):
        if not ctx['paramType']:
            raise SoftException('Missing parameter type for the CriticalDamageTooltip')
        model.setParamType(CriticalDamageTooltipModel.CRITICAL_DAMAGE)
        cls._packDetails(model.getDetails(), battleResults, ctx)

    @classmethod
    def _packDetails(cls, detailsModel, battleResults, ctx):
        detailsModel.clear()
        userName = ctx.get('userName')
        playerResults = getPlayerResults(battleResults, userName)
        crits = playerResults.critsInfo
        cls._packDetailsGroup(detailsModel, crits, CriticalDamageGroupModel.CRITICAL_DEVICES)
        cls._packDetailsGroup(detailsModel, crits, CriticalDamageGroupModel.DESTROYED_DEVICES)
        cls._packDetailsGroup(detailsModel, crits, CriticalDamageGroupModel.DESTROYED_TANKMENS)
        detailsModel.invalidate()

    @staticmethod
    def _packDetailsGroup(detailsModel, crits, groupType):
        for item in crits[groupType]:
            detailsGroupModel = CriticalDamageGroupModel()
            detailsGroupModel.setDamageGroup(groupType)
            detailsGroupModel.setValue(item)
            detailsModel.addViewModel(detailsGroupModel)
