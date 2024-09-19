# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/br_helper.py
from collections import namedtuple
import typing
from constants import ARENA_GUI_TYPE, ARENA_BONUS_TYPE, IS_DEVELOPMENT
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_results.br_constants import PremiumXpBonusRestrictions, EfficiencyKeys, EfficiencyItems, STAT_STUN_FIELD_NAMES
from gui.battle_results.components import style
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from dossiers2.ui.achievements import MARK_ON_GUN_RECORD, MARK_OF_MASTERY_RECORD
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.battle_results import IBattleResultsService
if typing.TYPE_CHECKING:
    from gui.battle_results.components.base import StatsBlock
    from gui.battle_results.reusable.players import PlayerInfo
    from gui.battle_results.reusable import _ReusableInfo
BattleResultData = namedtuple('BattleResultData', ('reusable', 'rawResult'))
_EnemyInfo = namedtuple('EnemyInfo', ('name', 'clanTag', 'tankName', 'shortVehicleName', 'vehicleType', 'value', 'isTeamKiller'))
_PlayerNames = namedtuple('PlayerNames', ('displayedName', 'hiddenName', 'isFakeNameVisible'))

def convertToDict(elems, defaultValue=0):
    return dict.fromkeys(elems, defaultValue)


def getAchievementCustomData(item):
    customData = []
    achievementName = item.getRecordName()
    if achievementName == MARK_ON_GUN_RECORD:
        customData.extend([item.getDamageRating(), item.getVehicleNationID()])
    if achievementName == MARK_OF_MASTERY_RECORD:
        customData.extend([item.getPrevMarkOfMastery(), item.getCompDescr()])
    return customData


def getArenaBonusType(reusable):
    return reusable.common.arenaBonusType


def getBattleType(reusable):
    arenaGuiType = reusable.common.arenaGuiType
    arenaType = reusable.common.arenaType
    return R.strings.arenas.type.dyn(arenaType.getGamePlayName()).name() if arenaGuiType in (ARENA_GUI_TYPE.RANDOM, ARENA_GUI_TYPE.EPIC_RANDOM) else R.strings.menu.loading.battleTypes.num(arenaGuiType)()


def getVehicleLevel(reusable):
    playerVehiclesIterator = reusable.personal.getVehicleItemsIterator()
    for _, vehicle in playerVehiclesIterator:
        return vehicle.level


def getShortVehicleInfo(reusable):
    playerInfo = reusable.getPlayerInfo()
    playerId = playerInfo.dbID
    vehicleId = reusable.vehicles.getVehicleID(playerId)
    vehicleInfo = reusable.vehicles.getVehicleInfo(vehicleId)
    return vehicleInfo


def getKillerID(result, vehicleCD):
    return result['personal'][vehicleCD].get('killerID', 0)


def getEnemies(reusable, result):
    enemies = []
    for _, enemies in reusable.getPersonalDetailsIterator(result['personal']):
        continue

    return enemies


def isPersonalResults(reusable, playerDBID):
    personalInfo = reusable.getPlayerInfo()
    return personalInfo.dbID == playerDBID


def isOwnSquad(reusable, vehicleID):
    personalInfo = reusable.getPlayerInfo()
    playerInfo = reusable.getPlayerInfoByVehicleID(vehicleID)
    personalPrebattleID = personalInfo.prebattleID if personalInfo.squadIndex else 0
    return personalPrebattleID != 0 and personalPrebattleID == playerInfo.prebattleID


def getUserNames(reusable, vehicleID):
    playerInfo = reusable.getPlayerInfoByVehicleID(vehicleID)
    if isBot(playerInfo):
        botName = backport.text(R.strings.event.postbattle_screen.botName())
        return _PlayerNames(displayedName=botName, hiddenName=botName, isFakeNameVisible=False)
    if not playerInfo.isAnonymized():
        return _PlayerNames(displayedName=playerInfo.realName, hiddenName=playerInfo.realName, isFakeNameVisible=False)
    isRealNameShown = isPersonalResults(reusable, playerInfo.dbID) or isOwnSquad(reusable, vehicleID)
    if isRealNameShown:
        displayedName = playerInfo.realName
        hiddenName = playerInfo.fakeName
    else:
        displayedName = playerInfo.fakeName
        hiddenName = playerInfo.realName
    return _PlayerNames(displayedName=displayedName, hiddenName=hiddenName, isFakeNameVisible=not isRealNameShown)


def isBot(playerInfo):
    return playerInfo.dbID == 0


def isPlayerLeftBattle(reusable):
    return reusable.personal.avatar.isPrematureLeave


@dependency.replace_none_kwargs(itemsCache=IItemsCache, battleResults=IBattleResultsService)
def isPremiumExpBonusAvailable(arenaUniqueID, isPersonalTeamWin, vehicleCD, itemsCache=None, battleResults=None):
    if battleResults.isAddXPBonusApplied(arenaUniqueID):
        restriction = PremiumXpBonusRestrictions.IS_APPLIED
    elif not isPersonalTeamWin:
        restriction = PremiumXpBonusRestrictions.IS_LOST_BATTLE
    elif not battleResults.isAddXPBonusEnabled(arenaUniqueID):
        restriction = PremiumXpBonusRestrictions.IS_BONUS_DISABLED
    elif _isBlockedByVehicle(vehicleCD, itemsCache=itemsCache):
        restriction = PremiumXpBonusRestrictions.IS_BLOCKED_BY_VEHICLE
    elif not battleResults.isXPToTManSameForArena(arenaUniqueID):
        if not battleResults.getVehicleForArena(arenaUniqueID).isXPToTman:
            restriction = PremiumXpBonusRestrictions.IS_XP_TO_TMEN_DISABLED
        else:
            restriction = PremiumXpBonusRestrictions.IS_XP_TO_TMEN_ENABLED
    elif not battleResults.isCrewSameForArena(arenaUniqueID):
        restriction = PremiumXpBonusRestrictions.IS_BLOCKED_BY_CREW
    else:
        restriction = PremiumXpBonusRestrictions.NO_RESTRICTION
    return restriction


def getDamageBlockDetails(damageDealt, piercings, labels):
    values = [backport.getIntegralFormat(damageDealt), backport.getIntegralFormat(piercings)]
    descriptions = [backport.text(labels[0], vals=style.getTooltipParamsStyle()), backport.text(labels[1])]
    return (values, descriptions)


def getArmorUsingDetails(rickochets, noDamage, damageBlocked, labels):
    values = [backport.getIntegralFormat(rickochets), backport.getIntegralFormat(noDamage), backport.getIntegralFormat(damageBlocked)]
    descriptions = [backport.text(labels[0]), backport.text(labels[1]), backport.text(labels[2], vals=style.getTooltipParamsStyle())]
    return (values, descriptions)


def getAssistBlockDetails(damageAssistedRadio, damageAssistedTrack, damageAssisted, labels):
    damageAssistedValues = [backport.getIntegralFormat(damageAssistedRadio), backport.getIntegralFormat(damageAssistedTrack), backport.getIntegralFormat(damageAssisted)]
    tooltipStyle = style.getTooltipParamsStyle()
    damageAssistedNames = [ backport.text(label, vals=tooltipStyle) for label in labels ]
    return (damageAssistedValues, damageAssistedNames)


def getStunBlockDetails(assisted, count, duration, labels):
    stunValues = [backport.getIntegralFormat(assisted), backport.getIntegralFormat(count), backport.getFractionalFormat(duration)]
    stunNames = [backport.text(labels[0], vals=style.getTooltipParamsStyle()), backport.text(labels[1]), backport.text(labels[2], vals=style.getTooltipParamsStyle(BATTLE_RESULTS.COMMON_TOOLTIP_PARAMS_VAL_SECONDS))]
    return (stunValues, stunNames)


def getCriticalDevicesBlock(crits, detailsBlock=None):
    _setNotEmptyForDetailsBlock(detailsBlock)
    criticalDevices = [ style.makeCriticalModuleTooltipLabel(device, count) for device, count in crits.iteritems() ]
    return style.makeMultiLineHtmlString(criticalDevices)


def getDestroyedDevicesBlock(crits, detailsBlock=None):
    _setNotEmptyForDetailsBlock(detailsBlock)
    destroyedDevices = [ style.makeDestroyedModuleTooltipLabel(device, count) for device, count in crits.iteritems() ]
    return style.makeMultiLineHtmlString(destroyedDevices)


def getDestroyedTankmenBlock(crits, detailsBlock=None):
    _setNotEmptyForDetailsBlock(detailsBlock)
    destroyedTankmen = [ style.makeTankmenTooltipLabel(tankman, count) for tankman, count in crits.iteritems() ]
    return style.makeMultiLineHtmlString(destroyedTankmen)


def getCaptureBlockDetails(capturePoints):
    captureValues = (backport.getIntegralFormat(capturePoints),)
    captureNames = (backport.text(R.strings.battle_results.common.tooltip.capture.totalPoints()),)
    return (captureValues, captureNames)


def getDefenceBlockDetails(defencePoints):
    defenceValues = (backport.getIntegralFormat(defencePoints),)
    defenceNames = (backport.text(R.strings.battle_results.common.tooltip.defence.totalPoints()),)
    return (defenceValues, defenceNames)


def getDefaultParameterValue(player, parameterName):
    return getattr(player, EfficiencyItems[parameterName][EfficiencyKeys.ENEMY_PARAM_NAME], 0)


def getStunParameterValue(player, _=None):
    return player.stunNum


def getDamageParameterValue(player, _=None):
    return player.piercings


def getArmorParameterValue(player, _=None):
    return player.noDamageDirectHitsReceived + player.rickochetsReceived


def checkStunParameterValue(player, _=None):
    for stunParameter in STAT_STUN_FIELD_NAMES:
        value = getattr(player, stunParameter)
        if value > 0:
            return value


def checkStunIconShown(player, _=None):
    return player.stunNum > 0


def checkDamageIconShown(player, _=None):
    return player.damageDealt > 0


def checkArmorIconShown(player, _=None):
    return player.noDamageDirectHitsReceived or player.rickochetsReceived or player.damageBlockedByArmor


def _setNotEmptyForDetailsBlock(detailsBlock):
    if detailsBlock is not None:
        detailsBlock.setEmpty(False)
    return


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _isBlockedByVehicle(vehicleCD, itemsCache=None):
    item = itemsCache.items.getItemByCD(vehicleCD)
    return not item.isInInventory or not item.activeInNationGroup


def _isDevBattle(reusable):
    arenaBonusType = reusable.common.arenaBonusType
    arenaGuiType = reusable.common.arenaGuiType
    return IS_DEVELOPMENT and arenaBonusType == ARENA_BONUS_TYPE.REGULAR and arenaGuiType == ARENA_GUI_TYPE.TRAINING
