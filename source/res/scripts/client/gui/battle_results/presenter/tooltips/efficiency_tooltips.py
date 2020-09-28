# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/tooltips/efficiency_tooltips.py
from collections import Counter
from frameworks.wulf import Array
from gui.battle_results.br_helper import getArenaBonusType, getEnemies, getDamageBlockDetails, getStunBlockDetails, getAssistBlockDetails, getCaptureBlockDetails, getDefenceBlockDetails, getCriticalDevicesBlock, getDestroyedDevicesBlock, getArmorUsingDetails, BattleResultData, convertToDict
from gui.battle_results.br_helper import getDestroyedTankmenBlock
from gui.battle_results.br_constants import EfficiencyKeys, EfficiencyItems
from gui.battle_results.reusable.shared import getPlayerPlaceInTeam
from gui.battle_results.presenter.common import setBaseUserInfo, setBaseEnemyVehicleInfo
from gui.shared.crits_mask_parser import CRIT_MASK_SUB_TYPES
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.enemy_with_one_param_model import EnemyWithOneParamModel
from gui.impl.gen.view_models.views.lobby.postbattle.tooltips.tooltip_efficiency_model import TooltipEfficiencyModel
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from shared_utils import findFirst
from soft_exception import SoftException

class TeamEfficiencyTooltipData(object):

    def __init__(self, effType):
        self.type = effType
        self.disabled = False
        self.isGarage = False
        self.values = []
        self.discript = []
        self.value = None
        self.critDamage = None
        self.critWound = None
        self.critDestruction = None
        self.allCritDamage = None
        self.allCritWound = None
        self.allCritDestruction = None
        self.totalItemsCount = None
        self.totalAssistedDamage = 0
        self.killReason = -1
        self.arenaType = 0
        self.deathReasons = None
        self.totalKilled = ''
        self.spotted = 0
        return

    def toDict(self):
        return self.__dict__.copy()

    def setBaseValues(self, value, descript, count=0):
        self.values = value
        self.discript = descript
        self.totalItemsCount = str(count)

    def setCritValues(self, damage, wound, destroyed, count):
        self.critDamage = damage
        self.critWound = wound
        self.critDestruction = destroyed
        self.totalItemsCount = count

    def setTotalCritValues(self, damage, destroyed, wound):
        self.allCritDamage = damage
        self.allCritWound = wound
        self.allCritDestruction = destroyed


def setPersonalEfficiencyTooltipData(model, parameterName, battleResult):
    reusable, result = battleResult
    info = reusable.getPersonalVehiclesInfo(result['personal'])
    total = getattr(info, parameterName)
    if 'event_boss' in info.vehicle.tags:
        total = 0
    rank = getPlayerPlaceInTeam(reusable, result, parameterName, total)
    enemies = getEnemies(reusable, result)
    enemyParamName = EfficiencyItems[parameterName][EfficiencyKeys.ENEMY_PARAM_NAME]
    enemyModelArray = Array()
    for enemy in enemies:
        if enemy.player.dbID == 0:
            continue
        paramValue = getattr(enemy, enemyParamName)
        if paramValue <= 0:
            continue
        enemyModel = EnemyWithOneParamModel()
        setBaseUserInfo(enemyModel.user, reusable, enemy.vehicleID)
        setBaseEnemyVehicleInfo(enemyModel, enemy)
        enemyModel.setValue(paramValue)
        enemyModelArray.addViewModel(enemyModel)

    model.setParamName(parameterName)
    model.setRank(rank)
    model.setEnemies(enemyModelArray)


def getTeamEfficiencyTooltipData(parameterName, enemyVehicleID, battleResult):
    reusable, result = battleResult
    if parameterName in (BATTLE_EFFICIENCY_TYPES.CAPTURE, BATTLE_EFFICIENCY_TYPES.DEFENCE):
        return _getBaseEfficiencyTooltipData(parameterName, reusable, result)
    elif not enemyVehicleID:
        return TeamEfficiencyTooltipData(EfficiencyItems[parameterName][EfficiencyKeys.TYPE])
    else:
        enemies = getEnemies(reusable, result)
        enemyResult = findFirst(lambda e: e.vehicleID == enemyVehicleID, enemies)
        if enemyResult is None:
            raise SoftException('Enemy with id {} not found'.format(enemyVehicleID))
        efficiencyGetter = EfficiencyGetter(parameterName)
        return efficiencyGetter.getEfficiencyTooltipData(enemyResult, battleResult)


def getTotalEfficiencyTooltipData(parameterName, battleResults):
    reusable, result = battleResults
    info = reusable.getPersonalVehiclesInfo(result['personal'])
    efficiencyGetter = TotalEfficiencyGetter(parameterName)
    return efficiencyGetter.getEfficiencyTooltipData(info, battleResults)


class EfficiencyGetter(object):
    __slots__ = ('__parameterName', '_tooltipData')

    def __init__(self, parameterName):
        self.__parameterName = parameterName
        self._tooltipData = None
        return

    def getEfficiencyTooltipData(self, playerResult, battleResults):
        efficiencyType = self.__getEfficiencyType()
        self._tooltipData = TeamEfficiencyTooltipData(efficiencyType)
        processor = self.__getProcessor().get(efficiencyType)
        if processor is None:
            raise SoftException('Processor is not found')
        processor(playerResult, battleResults)
        return self._tooltipData

    def _processSpotted(self, playerResult, _=None):
        pass

    def _processDamage(self, playerResult, _=None):
        damageDealtVals, damageDealtNames, damageTotalItems = self._getDamageBaseValues(playerResult)
        self._tooltipData.setBaseValues(damageDealtVals, damageDealtNames, damageTotalItems)

    def _processArmor(self, playerResult, battleResults):
        armorVals, armorNames, armorTotalItems = self._getArmorBaseValues(playerResult, battleResults)
        self._tooltipData.setBaseValues(armorVals, armorNames, armorTotalItems)

    def _processAssist(self, playerResult, _=None):
        damageAssistedVals, damageAssistedNames, assistTotalItems = self._getAssistBaseValues(playerResult)
        self._tooltipData.totalAssistedDamage = assistTotalItems
        self._tooltipData.setBaseValues(damageAssistedVals, damageAssistedNames, assistTotalItems)

    def _processCrits(self, playerResult, _=None):
        crits = playerResult.critsInfo
        criticalDevices = getCriticalDevicesBlock(convertToDict(crits[CRIT_MASK_SUB_TYPES.CRITICAL_DEVICES]))
        destroyedDevices = getDestroyedDevicesBlock(convertToDict(crits[CRIT_MASK_SUB_TYPES.DESTROYED_DEVICES]))
        destroyedTankmen = getDestroyedTankmenBlock(convertToDict(crits[CRIT_MASK_SUB_TYPES.DESTROYED_TANKMENS]))
        self._tooltipData.setCritValues(criticalDevices, destroyedTankmen, destroyedDevices, str(crits['critsCount']))

    def _processKilled(self, playerResult, battleResult=None):
        if playerResult.targetKills:
            self._tooltipData.killReason = playerResult.deathReason
            self._tooltipData.arenaType = getArenaBonusType(battleResult.reusable)

    def _processStun(self, playerResult, _=None):
        stunVals, stunNames, stunTotalItems = self._getStunBaseValues(playerResult)
        self._tooltipData.setBaseValues(stunVals, stunNames, stunTotalItems)

    @classmethod
    def _getStunBaseValues(cls, playerResult):
        count = playerResult.stunNum
        assisted = playerResult.damageAssistedStun
        duration = playerResult.stunDuration
        if count > 0 or assisted > 0 or duration > 0:
            labels = cls._getStunLabels()
            stunValues, stunNames = getStunBlockDetails(assisted, count, duration, labels)
            return (stunValues, stunNames, count)
        else:
            return (None, None, count)

    @classmethod
    def _getDamageBaseValues(cls, playerResult):
        piercings = playerResult.piercings
        damageDealt = playerResult.damageDealt
        if damageDealt > 0:
            labels = cls._getDamageLabels()
            values, descriptions = getDamageBlockDetails(damageDealt, piercings, labels)
            return (values, descriptions, piercings)
        else:
            return (None, None, piercings)

    @classmethod
    def _getArmorBaseValues(cls, playerResult, battleResults):
        noDamage = playerResult.noDamageDirectHitsReceived
        damageBlocked = playerResult.damageBlockedByArmor
        if noDamage > 0 or damageBlocked > 0:
            labels = cls._getArmorLabels()
            values, descriptions = getArmorUsingDetails(cls._getRickochets(playerResult, battleResults), noDamage, damageBlocked, labels)
            return (values, descriptions, noDamage)
        else:
            return (None, None, noDamage)

    @classmethod
    def _getAssistBaseValues(cls, playerResult):
        damageAssistedTrack = playerResult.damageAssistedTrack
        damageAssistedRadio = playerResult.damageAssistedRadio
        damageAssisted = damageAssistedTrack + damageAssistedRadio
        if damageAssisted > 0:
            labels = cls._getAssistLabels()
            damageAssistedValues, damageAssistedNames = getAssistBlockDetails(damageAssistedRadio, damageAssistedTrack, damageAssisted, labels)
            return (damageAssistedValues, damageAssistedNames, damageAssisted)
        else:
            return (None, None, damageAssisted)

    @classmethod
    def _getRickochets(cls, playerResult, _):
        return playerResult.rickochetsReceived

    @classmethod
    def _getStunLabels(cls):
        return (R.strings.battle_results.common.tooltip.stun.part1(), R.strings.battle_results.common.tooltip.stun.part2(), R.strings.battle_results.common.tooltip.stun.part3())

    @classmethod
    def _getAssistLabels(cls):
        return (R.strings.battle_results.common.tooltip.assist.part1(), R.strings.battle_results.common.tooltip.assist.part2(), R.strings.battle_results.common.tooltip.assist.total())

    @classmethod
    def _getArmorLabels(cls):
        return (R.strings.battle_results.common.tooltip.armor.part1(), R.strings.battle_results.common.tooltip.armor.part2(), R.strings.battle_results.common.tooltip.armor.part3())

    @classmethod
    def _getDamageLabels(cls):
        return (R.strings.battle_results.common.tooltip.damage.part1(), R.strings.battle_results.common.tooltip.damage.part2())

    def __getProcessor(self):
        return {BATTLE_EFFICIENCY_TYPES.DAMAGE: self._processDamage,
         BATTLE_EFFICIENCY_TYPES.ARMOR: self._processArmor,
         BATTLE_EFFICIENCY_TYPES.ASSIST: self._processAssist,
         BATTLE_EFFICIENCY_TYPES.CRITS: self._processCrits,
         BATTLE_EFFICIENCY_TYPES.DESTRUCTION: self._processKilled,
         BATTLE_EFFICIENCY_TYPES.TEAM_DESTRUCTION: self._processKilled,
         BATTLE_EFFICIENCY_TYPES.ASSIST_STUN: self._processStun,
         BATTLE_EFFICIENCY_TYPES.DETECTION: self._processSpotted}

    def __getEfficiencyType(self):
        return EfficiencyItems[self.__parameterName][EfficiencyKeys.TYPE]


class TotalEfficiencyGetter(EfficiencyGetter):

    def _processSpotted(self, info, _=None):
        self._tooltipData.spotted = info.spotted

    def _processKilled(self, playerResult, battleResults=None):
        reusable, result = battleResults
        allReasons = Counter([ enemy.deathReason for enemy in getEnemies(reusable, result) if enemy.targetKills and enemy.deathReason >= 0 ])
        self._tooltipData.deathReasons = allReasons

    def _processCrits(self, playerResult, battleResult=None):
        criticalDevices = self.__getAllDestroyedObjects(CRIT_MASK_SUB_TYPES.CRITICAL_DEVICES, battleResult)
        destroyedDevices = self.__getAllDestroyedObjects(CRIT_MASK_SUB_TYPES.DESTROYED_DEVICES, battleResult)
        destroyedTankmen = self.__getAllDestroyedObjects(CRIT_MASK_SUB_TYPES.DESTROYED_TANKMENS, battleResult)
        allCriticalDevices = getCriticalDevicesBlock(criticalDevices)
        allDestroyedDevices = getDestroyedDevicesBlock(destroyedDevices)
        allDestroyedTankmen = getDestroyedTankmenBlock(destroyedTankmen)
        self._tooltipData.setTotalCritValues(allCriticalDevices, allDestroyedDevices, allDestroyedTankmen)

    @classmethod
    def _getRickochets(cls, playerResult, battleResults):
        return sum([ enemy.rickochetsReceived for enemy in getEnemies(battleResults.reusable, battleResults.rawResult) ])

    @classmethod
    def _getStunLabels(cls):
        return (R.strings.postbattle_screen.tooltip.stun.totalDamage(), R.strings.postbattle_screen.tooltip.stun.totalCount(), R.strings.postbattle_screen.tooltip.stun.totalTime())

    @classmethod
    def _getAssistLabels(cls):
        return (R.strings.postbattle_screen.tooltip.assist.damageAssistedRadio(), R.strings.postbattle_screen.tooltip.assist.damageAssistedTrack(), R.strings.postbattle_screen.tooltip.assist.totalDamageAssisted())

    @classmethod
    def _getArmorLabels(cls):
        return (R.strings.postbattle_screen.tooltip.armor.totalRicochets(), R.strings.postbattle_screen.tooltip.armor.totalNotPierced(), R.strings.postbattle_screen.tooltip.armor.totalBlockedDamage())

    @classmethod
    def _getDamageLabels(cls):
        return (R.strings.postbattle_screen.tooltip.damage.totalDamage(), R.strings.postbattle_screen.tooltip.damage.totalPierced())

    @staticmethod
    def __getAllDestroyedObjects(parameter, battleResult):
        return Counter([ item for enemy in getEnemies(*battleResult) for item in enemy.critsInfo[parameter] ])


def _getBaseEfficiencyTooltipData(efficiencyType, reusable, rawResult):
    if efficiencyType == BATTLE_EFFICIENCY_TYPES.CAPTURE:
        accessor = _getCaptureBaseValues
    elif efficiencyType == BATTLE_EFFICIENCY_TYPES.DEFENCE:
        accessor = _getDefenceBaseValues
    else:
        raise SoftException('Incorrect efficiency type {} for the base parameter'.format(efficiencyType))
    tooltipData = TeamEfficiencyTooltipData(efficiencyType)
    result = reusable.vehicles.getVehicleSummarizeInfo(reusable.getPlayerInfo(), rawResult['vehicles'])
    values, names, totals = accessor(result)
    tooltipData.setBaseValues(values, names, totals)
    return tooltipData


def _getCaptureBaseValues(result):
    capturePoints = result.capturePoints
    if capturePoints > 0:
        captureValues, captureNames = getCaptureBlockDetails(capturePoints)
        return (captureValues, captureNames, capturePoints)
    else:
        return (None, None, capturePoints)


def _getDefenceBaseValues(result):
    defencePoints = result.droppedCapturePoints
    if defencePoints > 0:
        defenceValues, defenceNames = getDefenceBlockDetails(defencePoints)
        return (defenceValues, defenceNames, defencePoints)
    else:
        return (None, None, defencePoints)
