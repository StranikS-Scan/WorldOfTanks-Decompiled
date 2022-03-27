# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_helpers.py
import logging
from enum import unique, Enum
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import time_formatters, text_styles
from gui.periodic_battles.models import AlertData, PrimeTimeStatus
from helpers import dependency, i18n, time_utils
from items import vehicles
from items.components.supply_slot_categories import SlotCategories
from shared_utils import first
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IEpicBattleMetaGameController
_logger = logging.getLogger(__name__)
FRONTLINE_HIDDEN_TAG = 'fr_hidden'
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
           'delay-recon': 'Deployment_ReconFlight',
           '#epic_battle:abilityInfo/params/recon/revealedArea/value': 'Revealed Area',
           'entitiesToSearch/Vehicle/spottingDuration': 'Spotting Duration'},
 'inspire': {'cooldownTime': 'Cooldown',
             'radius': 'Effect Radius',
             'duration-inspire': 'Duration',
             'increaseFactors/crewRolesFactor': 'Crew Performance',
             'selfIncreaseFactors/crewRolesFactor': 'Self crew Perfomance',
             'inactivationDelay': 'Effect Cooldown'},
 'smoke': {'cooldownTime': 'Cooldown',
           'minDelay': 'Deployment',
           'areaLength_areaWidth-targetedArea': 'Targeted Area (length, width)',
           'projectilesNumber': 'Grenades',
           'totalDuration': 'Smoke Lifetime',
           'attrFactorMods/circularVisionRadius': 'visionRadiusFactor',
           'attrFactorMods/crewRolesFactor': 'crewRoles'},
 'passive_engineering': {'resupplyCooldownFactor': 'Resupply Circle Refresh',
                         'resupplyHealthPointsFactor': 'Resupply Speed',
                         'captureSpeedFactor': 'Capture Speed',
                         'captureBlockBonusTime': 'Capture Block Time',
                         'resupplyShellsFactor': 'Speed of shells supply'},
 'arcade_minefield': {'cooldownTime': 'Cooldown',
                      'bombsNumber-minefield': 'Mines',
                      'mineParams/lifetime': 'Duration_MineField',
                      'mineParams/shell': 'Stun'},
 'regenerationKit': {'cooldownTime': 'Cooldown',
                     'healTime': 'HealTime',
                     'healthRegenPerTick': 'RegenPerTick',
                     'initialHeal': 'InitialHeal',
                     'resupplyHealthPointsFactor': 'ResupplyHealthPointsFactor',
                     '#epic_battle:abilityInfo/params/fl_regenerationKit/minesDamageReduceFactor/value': 'MinesDamageReduceFactor'},
 'stealthRadar': {'passiveCircularVisionRadius': 'PassiveCircularVisionRadius',
                  'duration-stealth_radar': 'Duration_Stealth',
                  'cooldownTime': 'Cooldown',
                  'inactivationDelay': 'ActivationDelay',
                  'overridableFactors/invisibility': 'InvisibilityAdditiveTerm',
                  'increaseFactors/demaskMovingFactor': 'DemaskMovingFactor',
                  'increaseFactors/demaskFoliageFactor': 'DemaskFoliageFactor'}}

@unique
class EpicBattleScreens(Enum):
    RESERVES = 'reserves/'

    @classmethod
    def hasValue(cls, value):
        return value in cls.__members__.values()


def _getAttrName(param):
    return param.split('-')[0]


def _cutDigits(value):
    if abs(value) > 99:
        return round(value)
    return round(value, 1) if abs(value) > 9 else round(value, 3)


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
        params = param.split('/')
        curValue = cls._getEqParam(curEq, params)
        return _getFormattedNum(curValue)

    @classmethod
    def _getEqParam(cls, eq, params):
        data = {}
        if hasattr(eq, params[0]):
            data = getattr(eq, params[0])
        for key in params[1:]:
            if isinstance(data, dict):
                data = data.get(key, {})
            if hasattr(data, key):
                data = getattr(data, key)

        return data


class PercentValueMixin(DirectValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        value = super(PercentValueMixin, cls)._getParamValue(curEq, param)
        return value * 100 - 100


class AbsPercentValueMixin(DirectValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        value = super(AbsPercentValueMixin, cls)._getParamValue(curEq, param)
        return abs(value * 100 - 100)


class NestedPercentValueMixin(NestedValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        value = super(NestedPercentValueMixin, cls)._getParamValue(curEq, param)
        return value * 100 - 100


class NestedAbsPercentTupleValueMixin(NestedValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        param = _getAttrName(param)
        params = param.split('/')
        curValue = cls._getEqParam(curEq, params)
        return abs(_getFormattedNum(curValue[0]) * 100)


class DirectPercentValueMixin(DirectValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        value = super(DirectPercentValueMixin, cls)._getParamValue(curEq, param)
        return value * 100


class NestedDirectPercentValueMixin(NestedValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        value = super(NestedDirectPercentValueMixin, cls)._getParamValue(curEq, param)
        return value * 100


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


class NestedShellStunValuesMixin(NestedValuesMixin):

    @classmethod
    def _getParamValue(cls, curEq, param):
        curValue = 0
        shellID = super(NestedShellStunValuesMixin, cls)._getParamValue(curEq, param)
        curShell = vehicles.getItemByCompactDescr(shellID)
        if curShell:
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
        return cls._getParamValue(curEq, param)


class MultiTextParam(AbilityParam, DisplayValuesMixin):

    @classmethod
    def updateParams(cls, curEq, param):
        values = cls._getParamValue(curEq, param)
        unitLocalization = backport.text(R.strings.ingame_gui.marker.meters())
        value = ' x '.join((str(value) for value in values))
        value = '{} {}'.format(value, unitLocalization)
        return value


class FixedTextParam(AbilityParam):

    @classmethod
    def updateParams(cls, curEq, param):
        return i18n.makeString(param)


class DirectNumericTextParam(TextParam, DirectValuesMixin):
    pass


class DirectSecondsTextParam(TextParam, DirectValuesMixin):
    pass


class DirectMetersTextParam(TextParam, DirectValuesMixin):
    pass


class NestedNumericTextParam(TextParam, NestedValuesMixin):
    pass


class NestedMetersTextParam(TextParam, NestedValuesMixin):
    pass


class PercentNumericTextParam(TextParam, PercentValueMixin):
    pass


class AbsPercentNumericTextParam(TextParam, AbsPercentValueMixin):
    pass


class NestedPercentNumericTextParam(TextParam, NestedPercentValueMixin):
    pass


class NestedAbsPercentNumbericTextParam(TextParam, NestedAbsPercentTupleValueMixin):
    pass


class DirectPercentNumericTextParam(TextParam, DirectPercentValueMixin):
    pass


class NestedDirectPercentNumericTextParam(TextParam, NestedDirectPercentValueMixin):
    pass


class ReciprocalNumericTextParam(TextParam, ReciprocalValuesMixin):
    pass


class ShellStunSecondsDeltaBarParam(TextParam, ShellStunValuesMixin):
    pass


class NestedShellStunSecondsDeltaBarParam(TextParam, NestedShellStunValuesMixin):
    pass


class MultipleMetersTextParam(MultiTextParam, MultiValuesMixin):
    pass


epicEquipmentParameterFormaters = {'cooldownTime': DirectNumericTextParam.updateParams,
 'delay': DirectNumericTextParam.updateParams,
 'delay-recon': DirectNumericTextParam.updateParams,
 'areaRadius': DirectNumericTextParam.updateParams,
 'shotsNumber': DirectNumericTextParam.updateParams,
 'duration-inspire': DirectNumericTextParam.updateParams,
 'duration-artillery': DirectNumericTextParam.updateParams,
 'areaLength_areaWidth-targetedArea': MultipleMetersTextParam.updateParams,
 'areaLength_areaWidth-dropArea': MultipleMetersTextParam.updateParams,
 'bombsNumber': DirectNumericTextParam.updateParams,
 'shellCompactDescr': ShellStunSecondsDeltaBarParam.updateParams,
 '#epic_battle:abilityInfo/params/recon/revealedArea/value': FixedTextParam.updateParams,
 'entitiesToSearch/Vehicle/spottingDuration': NestedNumericTextParam.updateParams,
 'minDelay': DirectNumericTextParam.updateParams,
 'projectilesNumber': DirectNumericTextParam.updateParams,
 'totalDuration': DirectNumericTextParam.updateParams,
 'increaseFactors[crewRolesFactor]': NestedPercentNumericTextParam.updateParams,
 'inactivationDelay': DirectNumericTextParam.updateParams,
 'resupplyCooldownFactor': ReciprocalNumericTextParam.updateParams,
 'resupplyHealthPointsFactor': PercentNumericTextParam.updateParams,
 'captureSpeedFactor': PercentNumericTextParam.updateParams,
 'captureBlockBonusTime': DirectNumericTextParam.updateParams,
 'mineParams/lifetime': NestedNumericTextParam.updateParams,
 'mineParams/shell': NestedShellStunSecondsDeltaBarParam.updateParams,
 'healTime': DirectNumericTextParam.updateParams,
 'healthRegenPerTick': DirectPercentNumericTextParam.updateParams,
 'initialHeal': DirectPercentNumericTextParam.updateParams,
 'duration-stealth_radar': DirectSecondsTextParam.updateParams,
 'overridableFactors/invisibility': NestedDirectPercentNumericTextParam.updateParams,
 'increaseFactors/demaskMovingFactor': NestedPercentNumericTextParam.updateParams,
 'increaseFactors/demaskFoliageFactor': NestedPercentNumericTextParam.updateParams,
 'passiveCircularVisionRadius': DirectMetersTextParam.updateParams,
 'bombsNumber-minefield': DirectNumericTextParam.updateParams,
 'increaseFactors/crewRolesFactor': NestedPercentNumericTextParam.updateParams,
 'selfIncreaseFactors/crewRolesFactor': NestedPercentNumericTextParam.updateParams,
 'resupplyShellsFactor': PercentNumericTextParam.updateParams,
 '#epic_battle:abilityInfo/params/fl_regenerationKit/minesDamageReduceFactor/value': FixedTextParam.updateParams,
 'attrFactorMods/circularVisionRadius': NestedAbsPercentNumbericTextParam.updateParams,
 'attrFactorMods/crewRolesFactor': NestedAbsPercentNumbericTextParam.updateParams,
 'radius': DirectMetersTextParam.updateParams}

def checkIfVehicleIsHidden(intCD):
    return FRONTLINE_HIDDEN_TAG in vehicles.getVehicleType(intCD).tags


@dependency.replace_none_kwargs(epicController=IEpicBattleMetaGameController)
def isVehLevelUnlockableInBattle(vehLevel, epicController=None):
    return vehLevel in epicController.getModeSettings().unlockableInBattleVehLevels


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
        skillInfo['price'] = skillData.price
        skillInfo['category'] = first(SlotCategories.ALL.intersection(skillData.tags))
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


def getTimeToEndStr(timeStamp):
    return backport.text(R.strings.epic_battle.tooltips.timeToEnd(), timeLeft=_getTimeLeftStr(timeStamp))


def getTimeToStartStr(timeStamp):
    return backport.text(R.strings.epic_battle.tooltips.timeToStart(), timeLeft=_getTimeLeftStr(timeStamp))


@dependency.replace_none_kwargs(epicController=IEpicBattleMetaGameController)
def getAlertStatusVO(epicController=None):
    status, timeLeft, _ = epicController.getPrimeTimeStatus()
    showPrimeTimeAlert = status != PrimeTimeStatus.AVAILABLE
    hasAvailableServers = epicController.hasAvailablePrimeTimeServers()
    return AlertData(alertIcon=backport.image(R.images.gui.maps.icons.library.alertBigIcon()) if showPrimeTimeAlert else None, buttonIcon='', buttonLabel=backport.text(R.strings.epic_battle.widgetAlertMessageBlock.button()), buttonVisible=showPrimeTimeAlert and hasAvailableServers, buttonTooltip=None, statusText=_getAlertStatusText(timeLeft, hasAvailableServers), popoverAlias=None, bgVisible=True, shadowFilterVisible=showPrimeTimeAlert, tooltip=None, isSimpleTooltip=False)


@dependency.replace_none_kwargs(epicController=IEpicBattleMetaGameController, connectionMgr=IConnectionManager)
def _getAlertStatusText(timeLeft, hasAvailableServers, connectionMgr=None, epicController=None):
    rAlertMsgBlock = R.strings.epic_battle.widgetAlertMessageBlock
    alertStr = ''
    if hasAvailableServers:
        alertStr = backport.text(rAlertMsgBlock.somePeripheriesHalt(), serverName=connectionMgr.serverUserNameShort)
    else:
        currSeason = epicController.getCurrentSeason()
        currTime = time_utils.getCurrentLocalServerTimestamp()
        primeTime = epicController.getPrimeTimes().get(connectionMgr.peripheryID)
        isCycleNow = currSeason and currSeason.hasActiveCycle(currTime) and primeTime and primeTime.getPeriodsBetween(currTime, currSeason.getCycleEndDate())
        if isCycleNow:
            if connectionMgr.isStandalone():
                key = rAlertMsgBlock.singleModeHalt
            else:
                key = rAlertMsgBlock.allPeripheriesHalt
            timeLeftStr = time_formatters.getTillTimeByResource(timeLeft, R.strings.epic_battle.status.timeLeft, removeLeadingZeros=True)
            alertStr = backport.text(key(), time=timeLeftStr)
        else:
            nextSeason = currSeason or epicController.getNextSeason()
            if nextSeason is not None:
                nextCycle = nextSeason.getNextByTimeCycle(currTime)
                if nextCycle is not None:
                    if nextCycle.announceOnly:
                        alertStr = backport.text(rAlertMsgBlock.announcement())
                    else:
                        timeLeftStr = time_formatters.getTillTimeByResource(nextCycle.startDate - currTime, R.strings.epic_battle.status.timeLeft, removeLeadingZeros=True)
                        alertStr = backport.text(rAlertMsgBlock.startIn(), time=timeLeftStr)
            if not alertStr:
                prevSeason = currSeason or epicController.getPreviousSeason()
                if prevSeason is not None:
                    prevCycle = prevSeason.getLastActiveCycleInfo(currTime)
                    if prevCycle is not None:
                        alertStr = backport.text(rAlertMsgBlock.noCycleMessage())
    return text_styles.vehicleStatusCriticalText(alertStr)


def _getTimeLeftStr(timeStamp):
    timeLeft = time_formatters.getTillTimeByResource(timeStamp, R.strings.menu.Time.timeLeftShort, removeLeadingZeros=True)
    return text_styles.stats(timeLeft)
