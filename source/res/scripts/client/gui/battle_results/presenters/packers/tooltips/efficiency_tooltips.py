# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/tooltips/efficiency_tooltips.py
import typing
import logging
from constants import DEATH_REASON_ALIVE
from frameworks.wulf.view.array import fillResourcesArray
from gui.battle_results.pbs_helpers.common import getEnemies
from gui.battle_results.presenters.packers.interfaces import ITooltipPacker
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.battle_results.personal_efficiency_model import EfficiencyParameter
from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.efficiency_item_model import Unit, EfficiencyItemModel
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.battle_results.reusable import _ReusableInfo
    from gui.battle_results.reusable.shared import VehicleSummarizeInfo
    from gui.impl.gen_utils import DynAccessor
    from gui.impl.gen.view_models.views.lobby.battle_results.tooltips.efficiency_tooltip_model import EfficiencyTooltipModel
_logger = logging.getLogger(__name__)
_STR_PATH = R.strings.battle_results.common
_IMG_PATH = R.images.gui.maps.icons.library.efficiency.statsParameters

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
    return (damageAssistedTrack, damageAssistedRadio, total) if isZeroValuesVisible or total > 0 else None


def getKilledReasons(reusable, results, isZeroValuesVisible=False):
    allReasons = [ enemy.deathReason for enemy in getEnemies(reusable, results) if enemy.targetKills and enemy.deathReason >= DEATH_REASON_ALIVE ]
    return allReasons if isZeroValuesVisible and len(allReasons) == 1 else None


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


class TotalSpottedParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.spotted.header
    _DESCRIPTION = _STR_PATH.tooltip.spotted.description
    _ICON = _IMG_PATH.spotted


class TotalCapturePointsParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.capture.header
    _DESCRIPTION = _STR_PATH.tooltip.capture.description
    _ICON = _IMG_PATH.capturePoints


class TotalDefencePointsParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.defence.header
    _DESCRIPTION = _STR_PATH.tooltip.defence.description
    _ICON = _IMG_PATH.droppedCapturePoints


class TotalKillsParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.kill.header
    _DESCRIPTION = _STR_PATH.tooltip.killCommon.description
    _ICON = _IMG_PATH.kills
    _STATUS = _STR_PATH.tooltip

    @classmethod
    def getStatuses(cls, reusable, results, isZeroValuesVisible=False):
        reasons = getKilledReasons(reusable, results, isZeroValuesVisible)
        if not reasons:
            return None
        else:
            statuses = []
            for deathReason in reasons:
                killStatus = cls._STATUS.dyn('kill{}'.format(deathReason))
                if killStatus != R.invalid():
                    statuses.append(killStatus.description())

            return statuses


class TotalDamageDealtParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.damage.header
    _DESCRIPTION = _STR_PATH.tooltip.damage.description
    _ICON = _IMG_PATH.damageDealt
    _ITEM_LABELS = ((_STR_PATH.totalTooltip.damage.part1, Unit.COUNT), (_STR_PATH.totalTooltip.damage.part2, None))

    @classmethod
    def getValues(cls, playerResult, isZeroValuesVisible=False):
        return getDamageValues(playerResult, isZeroValuesVisible)


class TotalStunParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.stun.header
    _DESCRIPTION = _STR_PATH.tooltip.stun.description
    _ICON = _IMG_PATH.damageAssistedStun
    _ITEM_LABELS = ((_STR_PATH.totalTooltip.stun.part1, Unit.COUNT), (_STR_PATH.totalTooltip.stun.part2, None), (_STR_PATH.totalTooltip.stun.part3, Unit.SEC))

    @classmethod
    def getValues(cls, playerResult, isZeroValuesVisible=False):
        return getStunValues(playerResult, isZeroValuesVisible)


class TotalDamageAssistedParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.assist.header
    _DESCRIPTION = _STR_PATH.tooltip.assist.description
    _ICON = _IMG_PATH.damageAssisted
    _ITEM_LABELS = ((_STR_PATH.totalTooltip.assist.part1, Unit.COUNT), (_STR_PATH.totalTooltip.assist.part2, Unit.COUNT), (_STR_PATH.totalTooltip.assist.total, Unit.COUNT))

    @classmethod
    def getValues(cls, playerResult, isZeroValuesVisible=False):
        return getAssistValues(playerResult, isZeroValuesVisible)


class TotalDamageBlockedByArmorParameter(BaseParameter):
    _TITLE = _STR_PATH.tooltip.armor.header
    _DESCRIPTION = _STR_PATH.tooltip.armor.description
    _ICON = _IMG_PATH.damageBlockedByArmor
    _ITEM_LABELS = ((_STR_PATH.totalTooltip.armor.part1, None), (_STR_PATH.totalTooltip.armor.part2, None), (_STR_PATH.totalTooltip.armor.part3, Unit.COUNT))

    @classmethod
    def getValues(cls, playerResult, isZeroValuesVisible=False):
        return getArmorValues(playerResult, isZeroValuesVisible)


PARAMETERS_TO_TOOLTIP_MAP = {EfficiencyParameter.STUN: TotalStunParameter,
 EfficiencyParameter.DAMAGEDEALT: TotalDamageDealtParameter,
 EfficiencyParameter.DAMAGEBLOCKEDBYARMOR: TotalDamageBlockedByArmorParameter,
 EfficiencyParameter.DAMAGEASSISTED: TotalDamageAssistedParameter,
 EfficiencyParameter.SPOTTED: TotalSpottedParameter,
 EfficiencyParameter.KILLS: TotalKillsParameter,
 EfficiencyParameter.CAPTUREPOINTS: TotalCapturePointsParameter,
 EfficiencyParameter.DROPPEDCAPTUREPOINTS: TotalDefencePointsParameter}

class EfficiencyTooltipsPacker(ITooltipPacker):
    __slots__ = ()
    _TOOLTIPS = PARAMETERS_TO_TOOLTIP_MAP

    @classmethod
    def packTooltip(cls, model, battleResults, ctx=None):
        if ctx is None or 'paramType' not in ctx:
            _logger.error('Missing parameter type for the EfficiencyTooltip')
            return
        else:
            paramType = ctx['paramType']
            reusable, results = battleResults.reusable, battleResults.results
            playerResults = reusable.getPersonalVehiclesInfo(results['personal'])
            parameter = EfficiencyParameter(paramType)
            tooltipHelper = cls._TOOLTIPS.get(parameter)
            if tooltipHelper is not None:
                model.setTitle(tooltipHelper.getTitle()())
                model.setDescription(tooltipHelper.getDescription()())
                model.setIcon(tooltipHelper.getIcon()())
                values = tooltipHelper.getValues(playerResults, True)
                if values is not None:
                    cls.__packDetails(model.getDetails(), values, tooltipHelper.getLables())
                statuses = tooltipHelper.getStatuses(reusable, results, True)
                if statuses is not None:
                    fillResourcesArray(statuses, model.getStatuses())
            return

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
