# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_helpers.py
import re
import logging
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.processors.common import EpicPrestigeTrigger, EpicPrestigePointsExchange
from gui.shared.items_parameters.formatters import _cutDigits
from gui.shared.utils import decorators
from helpers import dependency, i18n
from items import vehicles
from shared_utils import first
from skeletons.gui.game_control import IEpicBattleMetaGameController, IEventProgressionController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
FRONTLINE_HIDDEN_TAG = 'fr_hidden'
FRONTLINE_VEH_BOUGHT_TOKEN_TEMPLATE = 'fr_reward_%s'
NESTED_VALUE_REGEX = '(?P<obj>.*)\\[(?P<param>.*)\\]'
_EPIC_GAME_PARAMS = {'artillery': {'cooldownTime': 'Cooldown',
               'delay': 'Deployment',
               'areaRadius': 'Dispersion',
               'shotsNumber': 'Shells',
               'duration-artillery': 'Duration'},
 'bomber': {'cooldownTime': 'Cooldown',
            'delay': 'Deployment',
            'areaLength_areaWidth-dropArea': 'Targeted Area',
            'bombsNumber': 'Bombs',
            'shellCompactDescr': 'Stun'},
 'recon': {'cooldownTime': 'Cooldown',
           'delay': 'Deployment',
           '#epic_battle:abilityInfo/params/recon/revealedArea/value': 'Revealed Area',
           'spottingDuration': 'Spotting Duration'},
 'inspire': {'cooldownTime': 'Cooldown',
             'radius': 'Effect Radius',
             'duration-inspire': 'Duration',
             'increaseFactors[crewRolesFactor]': 'Crew Performance',
             'inactivationDelay': 'Effect Cooldown'},
 'smoke': {'cooldownTime': 'Cooldown',
           'minDelay': 'Deployment',
           'areaLength_areaWidth-targetedArea': 'Targeted Area (length, width)',
           'projectilesNumber': 'Grenades',
           'totalDuration': 'Smoke Lifetime'},
 'passive_engineering': {'resupplyCooldownFactor': 'Resupply Circle Refresh',
                         'resupplyHealthPointsFactor': 'Resupply Speed',
                         'captureSpeedFactor': 'Capture Speed',
                         'captureBlockBonusTime': 'Capture Block Time'}}

def _getAttrName(param):
    return param.split('-')[0]


def _getFormattedNum(value):
    cutValue = _cutDigits(value)
    return int(cutValue) if cutValue.is_integer() else cutValue


class AbilityParam(object):

    @classmethod
    def updateParams(cls, curEq, param):
        raise NotImplementedError


class DisplayValuesMixin(object):

    @classmethod
    def _getParamValue(cls, curEq, param):
        raise NotImplementedError


class DirectValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        param = _getAttrName(param)
        curValue = getattr(curEq, param)
        return _getFormattedNum(curValue)


class NestedValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        param = _getAttrName(param)
        match = re.search(NESTED_VALUE_REGEX, param)
        obj = getattr(curEq, match.group('obj'))
        curValue = obj.get(match.group('param'))
        return _getFormattedNum(curValue)


class PercentValueMixin(DirectValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        value = super(PercentValueMixin, cls)._getParamValue(curEq, param)
        return value * 100 - 100


class NestedPercentValueMixin(NestedValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        value = super(NestedPercentValueMixin, cls)._getParamValue(curEq, param)
        return value * 100 - 100


class ReciprocalValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        param = _getAttrName(param)
        curValue = getattr(curEq, param)
        curValue = 1 / curValue if curValue != 0 else float('inf')
        curValue = curValue * 100 - 100
        return _getFormattedNum(curValue)


class ShellStunValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        param = _getAttrName(param)
        curShell = vehicles.getItemByCompactDescr(getattr(curEq, param))
        curValue = curShell.stun.stunDuration if curShell.hasStun else 0
        return _getFormattedNum(curValue)


class MultiValuesMixin(DisplayValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        param = _getAttrName(param)
        params = param.split('_')
        length = len(params)
        curValues = [None] * length
        for idx, singleParam in enumerate(params):
            curValues[idx] = _getFormattedNum(getattr(curEq, singleParam))

        return curValues


class TextParam(AbilityParam, DisplayValuesMixin):

    @classmethod
    def updateParams(cls, curEq, param):
        value = cls._getParamValue(curEq, param)
        return value


class MultiTextParam(AbilityParam, DisplayValuesMixin):

    @classmethod
    def updateParams(cls, curEq, param):
        values = cls._getParamValue(curEq, param)
        unitLocalization = backport.text(R.strings.ingame_gui.marker.meters())
        value = ' x '.join((str(value) for value in values))
        value = ''.join((value, unitLocalization))
        return value


class FixedTextParam(AbilityParam):

    @classmethod
    def updateParams(cls, curEq, param):
        return i18n.makeString(param)


class DirectNumericTextParam(TextParam, DirectValuesMixin):
    pass


class PercentNumericTextParam(TextParam, PercentValueMixin):
    pass


class NestedPercentNumericTextParam(TextParam, NestedPercentValueMixin):
    pass


class ReciprocalNumericTextParam(TextParam, ReciprocalValuesMixin):
    pass


class ShellStunSecondsDeltaBarParam(TextParam, ShellStunValuesMixin):
    pass


class MultipleMetersTextParam(MultiTextParam, MultiValuesMixin):
    pass


epicEquipmentParameterFormaters = {'cooldownTime': DirectNumericTextParam.updateParams,
 'delay': DirectNumericTextParam.updateParams,
 'areaRadius': DirectNumericTextParam.updateParams,
 'shotsNumber': DirectNumericTextParam.updateParams,
 'duration-inspire': DirectNumericTextParam.updateParams,
 'duration-artillery': DirectNumericTextParam.updateParams,
 'areaLength_areaWidth-targetedArea': MultipleMetersTextParam.updateParams,
 'areaLength_areaWidth-dropArea': MultipleMetersTextParam.updateParams,
 'bombsNumber': DirectNumericTextParam.updateParams,
 'shellCompactDescr': ShellStunSecondsDeltaBarParam.updateParams,
 '#epic_battle:abilityInfo/params/recon/revealedArea/value': FixedTextParam.updateParams,
 'spottingDuration': DirectNumericTextParam.updateParams,
 'minDelay': DirectNumericTextParam.updateParams,
 'projectilesNumber': DirectNumericTextParam.updateParams,
 'totalDuration': DirectNumericTextParam.updateParams,
 'radius': DirectNumericTextParam.updateParams,
 'increaseFactors[crewRolesFactor]': NestedPercentNumericTextParam.updateParams,
 'inactivationDelay': DirectNumericTextParam.updateParams,
 'resupplyCooldownFactor': ReciprocalNumericTextParam.updateParams,
 'resupplyHealthPointsFactor': PercentNumericTextParam.updateParams,
 'captureSpeedFactor': PercentNumericTextParam.updateParams,
 'captureBlockBonusTime': DirectNumericTextParam.updateParams}

def checkIfVehicleIsHidden(intCD):
    return FRONTLINE_HIDDEN_TAG in vehicles.getVehicleType(intCD).tags


def getFrontLineSkills():
    epicMetaGameCtrl = dependency.instance(IEpicBattleMetaGameController)
    equipments = vehicles.g_cache.equipments()
    result = []
    for skillID, skillData in epicMetaGameCtrl.getAllSkillsInformation().iteritems():
        skillInfo = dict()
        firstSkill = first(skillData.levels.itervalues())
        skillInfo['icon'] = firstSkill.icon
        skillInfo['longDescr'] = firstSkill.longDescr
        skillInfo['name'] = firstSkill.name
        skillInfo['shortDescr'] = firstSkill.shortDescr
        skillInfo['skillID'] = skillID
        skillInfo['longFilterAlert'] = firstSkill.longFilterAlert
        skillInfo['params'] = dict()
        for _, skillLevelData in skillData.levels.iteritems():
            skillInfo.setdefault('levels', []).append(skillLevelData.eqID)
            curLvlEq = equipments[skillLevelData.eqID]
            for tooltipIdentifier in curLvlEq.tooltipIdentifiers:
                paramName = _EPIC_GAME_PARAMS.get(skillLevelData.icon, {}).get(tooltipIdentifier)
                if not paramName:
                    _logger.error('[ERROR] getFrontLineSkills: Failed to find tooltipInfo %(ttid)s.', {'ttid': tooltipIdentifier})
                    continue
                param = createEpicParam(curLvlEq, tooltipIdentifier)
                if param:
                    skillInfo['params'].setdefault(paramName, []).append(param)
                skillInfo['params'].setdefault(paramName, [])

        result.append(skillInfo)

    return result


def createEpicParam(curLvlEq, tooltipIdentifier):
    formatter = epicEquipmentParameterFormaters.get(tooltipIdentifier)
    return formatter(curLvlEq, tooltipIdentifier) if formatter else None


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def checkEpicRewardVehAlreadyBought(vehIntCD, itemsCache=None):
    tokenName = FRONTLINE_VEH_BOUGHT_TOKEN_TEMPLATE % vehIntCD
    return tokenName in itemsCache.items.tokens.getTokens()


@decorators.process('updating')
def triggerPrestige():
    result = yield EpicPrestigeTrigger().request()
    if result.userMsg:
        SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)


@decorators.process('updating')
def exchangePrestigePoints():
    yield EpicPrestigePointsExchange().request()


def getFrontlineRewardVehPrice(intCD):
    eventProgCtrl = dependency.instance(IEventProgressionController)
    return {intCD:price for intCD, price in eventProgCtrl.rewardVehicles}.get(intCD, 0)
