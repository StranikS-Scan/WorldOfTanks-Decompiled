# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/battle_result/wt_battle_result_helpers.py
import typing
from collections import namedtuple
from gui.impl.gen import R
from gui.impl import backport
from gui.battle_control.battle_constants import WinStatus
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.postbattle.achievement_model import AchievementModel
from white_tiger.gui.impl.lobby.battle_result.team_stats import getTeamStats
from soft_exception import SoftException
from dossiers2.ui.achievements import ACHIEVEMENT_TYPE, MARK_OF_MASTERY, MARK_ON_GUN_RECORD, MARK_OF_MASTERY_RECORD
from shared_utils import CONST_CONTAINER
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from constants import DEATH_REASON_ALIVE
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.gui_items.Vehicle import getIconResourceName, getSimpleShortUserName
from gui.battle_results.reusable.shared import makeAchievement, makeMarkOfMasteryFromPersonal, VehicleSummarizeInfo
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
_AchievementData = namedtuple('_AchievementData', ('achievementID', 'name', 'isEpic', 'iconName', 'groupID', 'isPersonal'))
_FinancialRecords = namedtuple('_FinancialRecords', ('main', 'additional', 'alternative'))
_XpRecords = namedtuple('_XpRecords', ('xp', 'freeXP'))
_PlayerNames = namedtuple('PlayerNames', ('displayedName', 'hiddenName', 'isFakeNameVisible'))
MAX_TEAM_RANK = 3
STAT_STUN_FIELD_NAMES = ('damageAssistedStun', 'stunNum', 'stunDuration')

class PersonalEfficiency(CONST_CONTAINER):
    SPOTTED = 'spotted'
    KILLS = 'kills'
    STUN = 'damageAssistedStun'
    DAMAGE = 'damageDealt'
    ARMOR = 'damageBlockedByArmor'
    ASSIST = 'damageAssisted'
    CRITS = 'critsCount'
    ALL = (STUN,
     SPOTTED,
     ASSIST,
     ARMOR,
     CRITS,
     DAMAGE,
     KILLS)


class EfficiencyKeys(CONST_CONTAINER):
    ENEMY_PARAM_NAME = 'enemyParamName'
    TOTAL = 'summ'
    ICON = 'icon'
    TYPE = 'effType'


EfficiencyItems = {PersonalEfficiency.SPOTTED: {EfficiencyKeys.TOTAL: 'summSpotted',
                              EfficiencyKeys.ENEMY_PARAM_NAME: 'spotted',
                              EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.DETECTION},
 PersonalEfficiency.ASSIST: {EfficiencyKeys.TOTAL: 'summAssist',
                             EfficiencyKeys.ENEMY_PARAM_NAME: 'damageAssisted',
                             EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.ASSIST},
 PersonalEfficiency.ARMOR: {EfficiencyKeys.TOTAL: 'summArmor',
                            EfficiencyKeys.ENEMY_PARAM_NAME: 'damageBlockedByArmor',
                            EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.ARMOR},
 PersonalEfficiency.DAMAGE: {EfficiencyKeys.TOTAL: 'summDamage',
                             EfficiencyKeys.ENEMY_PARAM_NAME: 'damageDealt',
                             EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.DAMAGE},
 PersonalEfficiency.KILLS: {EfficiencyKeys.TOTAL: 'summKill',
                            EfficiencyKeys.ENEMY_PARAM_NAME: 'targetKills',
                            EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.DESTRUCTION},
 PersonalEfficiency.STUN: {EfficiencyKeys.TOTAL: 'summStun',
                           EfficiencyKeys.ENEMY_PARAM_NAME: 'damageAssistedStun',
                           EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.ASSIST_STUN},
 PersonalEfficiency.CRITS: {EfficiencyKeys.TOTAL: 'summCrits',
                            EfficiencyKeys.ENEMY_PARAM_NAME: 'critsCount',
                            EfficiencyKeys.TYPE: BATTLE_EFFICIENCY_TYPES.CRITS}}

def getKillerID(result, vehicleCD):
    return result['personal'][vehicleCD].get('killerID', 0)


def getPersonalTeamResult(reusable):
    winnerTeam = reusable.common.winnerTeam
    if not winnerTeam:
        return WinStatus.DRAW
    return WinStatus.WIN if winnerTeam == reusable.personal.avatar.team else WinStatus.LOSE


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


def _processAchievement(item, groupID):
    achievement = item.achievement
    achievementID = item.achievementID
    isPersonal = item.isPersonal
    return _AchievementData(achievementID=achievementID, name=achievement.getName(), isEpic=achievement.hasRibbon(), iconName=achievement.getIconName(), groupID=groupID, isPersonal=isPersonal)


def setTeamStatsAchievements(model, info):
    rawAchievements = info.getAchievements()
    processedAchievements = [ _processAchievement(item, AchievementModel.ACHIEVEMENT_RIGHT_BLOCK) for item in rawAchievements ]
    _setAchievements(processedAchievements, model)


def _setAchievements(processedAchievements, model):
    achievements = Array()
    for achievement in processedAchievements:
        achievementModel = AchievementModel()
        achievementModel.setName(achievement.name)
        achievementModel.setIsEpic(achievement.isEpic)
        achievementModel.setIconName(achievement.iconName)
        achievementModel.setGroupID(achievement.groupID)
        achievementModel.setAchievementID(achievement.achievementID)
        achievementModel.setIsPersonal(achievement.isPersonal)
        achievements.addViewModel(achievementModel)

    model.setAchievements(achievements)


class PostbattleFieldsGetter(object):
    __slots__ = ('__teamStats',)

    def __init__(self, teamStatsFields):
        self.__teamStats = teamStatsFields

    def clear(self):
        self.__teamStats = None
        return

    def getTeamStats(self, isSPG, isPersonal, isRoleExp):
        roleExpFields = (self.__teamStats.expSegments.total,
         self.__teamStats.expSegments.attack,
         self.__teamStats.expSegments.assist,
         self.__teamStats.expSegments.role)
        spgFields = (self.__teamStats.other.stunNum,
         self.__teamStats.other.stunDuration,
         self.__teamStats.other.damageAssistedStun,
         self.__teamStats.other.damageAssistedStunSelf)
        personalFields = (self.__teamStats.other.damageAssistedSelf, self.__teamStats.other.damageAssistedStunSelf)
        nonPersonalFields = (self.__teamStats.other.damageAssisted, self.__teamStats.other.damageAssistedStun)

        def filterFunc(field):
            return (field not in spgFields or isSPG) and (field not in personalFields or isPersonal) and (field not in nonPersonalFields or not isPersonal) and (field not in roleExpFields or isRoleExp)

        teamStats = self.__teamStats.expSegments + self.__teamStats.shots + self.__teamStats.damageDealt + self.__teamStats.hitsReceived + self.__teamStats.other + self.__teamStats.time
        for field in filter(filterFunc, teamStats):
            yield field


def createFieldsGetter():
    return PostbattleFieldsGetter(teamStatsFields=getTeamStats())


def getAchievementTooltipData(achievementID, achievementName, isPersonal, reusable, results):
    if not isPersonal:
        achievement = makeAchievement(achievementID)
    else:
        playerInfo = reusable.getPlayerInfo()
        playerId = playerInfo.dbID
        vehicleId = reusable.vehicles.getVehicleID(playerId)
        vehicleInfo = reusable.vehicles.getVehicleInfo(vehicleId)
        intCD = vehicleInfo.intCD
        if achievementName == MARK_OF_MASTERY:
            results = results['personal'][intCD]
            achievement = makeMarkOfMasteryFromPersonal(results)
            achievement.setPrevMarkOfMastery(results.get('prevMarkOfMastery', 0))
            achievement.setCompDescr(results.get('typeCompDescr'))
        else:
            achievement = makeAchievement(achievementID, results['personal'][intCD])
    if achievement is None:
        SoftException('Achievement with id={} is incorrect'.format(achievementID))
    return _packAchievementTooltipArgs(achievement, reusable)


def _packAchievementTooltipArgs(achievement, reusable):
    args = [achievement.getBlock(),
     achievement.getName(),
     achievement.getValue() if achievement.getType() != ACHIEVEMENT_TYPE.SERIES else 0,
     _getAchievementCustomData(achievement),
     _getVehicleLevel(reusable),
     reusable.common.arenaBonusType]
    return args


def _getVehicleLevel(reusable):
    playerVehiclesIterator = reusable.personal.getVehicleItemsIterator()
    for _, vehicle in playerVehiclesIterator:
        return vehicle.level


def _getAchievementCustomData(item):
    customData = []
    achievementName = item.getRecordName()
    if achievementName == MARK_ON_GUN_RECORD:
        customData.extend([item.getDamageRating(), item.getVehicleNationID()])
    if achievementName == MARK_OF_MASTERY_RECORD:
        customData.extend([item.getPrevMarkOfMastery(), item.getCompDescr()])
    return customData


def getPlayerPlaceInTeam(reusableInfo, result, paramName, playerValue):
    if playerValue == 0:
        return MAX_TEAM_RANK
    allies, _ = reusableInfo.getBiDirectionTeamsIterator(result['vehicles'])
    winners = set()
    for ally in allies:
        allyValue = getattr(ally, paramName)
        if allyValue > playerValue:
            winners.add(allyValue)
        if len(winners) >= MAX_TEAM_RANK:
            return MAX_TEAM_RANK

    return len(winners)


def getEnemies(reusable, result):
    enemies = []
    for _, enemies in reusable.getPersonalDetailsIterator(result['personal']):
        continue

    return enemies


def setBaseUserInfo(model, vehicleID, reusable):
    playerInfo = reusable.getPlayerInfoByVehicleID(vehicleID)
    model.setClanAbbrev(playerInfo.clanAbbrev)
    model.setIgrType(playerInfo.igrType)
    userNames = getUserNames(reusable, vehicleID)
    model.setUserName(userNames.displayedName)
    model.setHiddenUserName(userNames.hiddenName)
    model.setIsFakeNameVisible(userNames.isFakeNameVisible)
    shortVehicleInfo = reusable.vehicles.getVehicleInfo(vehicleID)
    model.setIsTeamKiller(shortVehicleInfo.isTeamKiller)
    model.setIsKilled(shortVehicleInfo.deathReason > DEATH_REASON_ALIVE)
    if playerInfo.dbID:
        setBadges(model, playerInfo.dbID, reusable)


def setBadges(model, playerDbID, reusable):
    if not playerDbID:
        return
    else:
        avatar = reusable.getAvatarInfo(playerDbID)
        if avatar is None:
            return
        badgeInfo = avatar.getFullBadgeInfo()
        if badgeInfo is not None:
            model.badge.setBadgeID(badgeInfo.getIconPostfix())
            level = badgeInfo.getDynamicContent()
            model.badge.setLevel(level if level is not None else '')
        suffixBadge = avatar.suffixBadge
        model.suffixBadge.setBadgeID(str(suffixBadge) if suffixBadge else '')
        return


def setBaseEnemyVehicleInfo(model, enemy):
    model.setTankType(replaceHyphenToUnderscore(enemy.vehicle.type))
    model.setTankName(replaceHyphenToUnderscore(getIconResourceName(enemy.vehicle.name)))
    model.setShortTankName(getSimpleShortUserName(enemy.vehicle))
    model.setVehicleIconName(getIconResourceName(enemy.vehicle.name))
    model.setVehicleLevel(enemy.vehicle.level)
