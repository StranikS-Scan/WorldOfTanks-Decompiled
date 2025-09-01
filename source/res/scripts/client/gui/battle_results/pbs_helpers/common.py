# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/pbs_helpers/common.py
import typing
import json
from itertools import chain
from collections import namedtuple
from constants import FINISH_REASON
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from dossiers2.ui.achievements import MARK_ON_GUN_RECORD, MARK_OF_MASTERY_RECORD, MARK_OF_MASTERY, MARK_ON_GUN, ACHIEVEMENT_TYPE
from gui.impl.gen.view_models.views.lobby.battle_results.postbattle_achievement_model import PostbattleAchievementModel
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
    from gui.battle_results.reusable.players import PlayerInfo
    from gui.battle_results.reusable.shared import VehicleSummarizeInfo
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.shared.gui_items.dossier.achievements.abstract import RegularAchievement
_PlayerNames = namedtuple('PlayerNames', ('displayedName', 'hiddenName', 'isFakeNameVisible'))

def isPersonalBattleResult(summarizeInfo, battleResult):
    return battleResult.reusable.getPlayerInfo().dbID == summarizeInfo.player.dbID


def isRealNameVisible(reusable, playerInfo):
    personalInfo = reusable.getPlayerInfo()
    isPersonalResult = personalInfo.dbID == playerInfo.dbID
    if isPersonalResult:
        return True
    personalPrebattleID = personalInfo.prebattleID if personalInfo.squadIndex else 0
    return personalPrebattleID != 0 and personalPrebattleID == playerInfo.prebattleID


def getArenaNameStr(reusable):
    accessor = R.strings.arenas.num(reusable.common.arenaType.getGeometryName())
    return backport.text(accessor.name()) if accessor.isValid() else backport.text(R.strings.arenas.invalid_map.name())


def getRegularFinishResultResource(finishReason, teamResult):
    isExtermination = finishReason == FINISH_REASON.EXTERMINATION
    reasonKey = 'c_{}{}'.format(finishReason, teamResult) if isExtermination else 'c_{}'.format(finishReason)
    return R.strings.battle_results.finish.reason.dyn(reasonKey)()


def getUserNames(playerInfo, isPlayerRealNameVisible):
    if not playerInfo.isAnonymized():
        return _PlayerNames(displayedName=playerInfo.realName, hiddenName=playerInfo.fakeName, isFakeNameVisible=False)
    if isPlayerRealNameVisible:
        displayedName = playerInfo.realName
        hiddenName = playerInfo.fakeName
    else:
        displayedName = playerInfo.fakeName
        hiddenName = playerInfo.realName
    return _PlayerNames(displayedName=displayedName, hiddenName=hiddenName, isFakeNameVisible=not isPlayerRealNameVisible)


def getEnemies(reusable, result):
    enemies = []
    for _, enemies in reusable.getPersonalDetailsIterator(result['personal']):
        continue

    return enemies


def pushNoBattleResultsDataMessage():
    SystemMessages.pushI18nMessage(BATTLE_RESULTS.NODATA, type=SystemMessages.SM_TYPE.Warning)


def getVehicleLevel(reusable):
    playerVehiclesIterator = reusable.personal.getVehicleItemsIterator()
    for _, vehicle in playerVehiclesIterator:
        return vehicle.level


_AchievementData = namedtuple('_AchievementData', ('name', 'isEpic', 'iconName', 'groupID', 'tooltipType', 'tooltipArgs'))

def getAchievementCustomData(item):
    customData = []
    achievementName = item.getRecordName()
    if achievementName == MARK_ON_GUN_RECORD:
        customData.extend([item.getDamageRating(), item.getVehicleNationID()])
    if achievementName == MARK_OF_MASTERY_RECORD:
        customData.extend([item.getPrevMarkOfMastery(), item.getCompDescr()])
    return customData


def getPersonalAchievements(battleResults):
    reusable, results = battleResults.reusable, battleResults.results
    left, right = reusable.personal.getAchievements(results['personal'])
    achievements = chain([ prepareAchievementData(item, PostbattleAchievementModel.ACHIEVEMENT_LEFT_BLOCK, reusable) for item in left ], [ prepareAchievementData(item, PostbattleAchievementModel.ACHIEVEMENT_RIGHT_BLOCK, reusable) for item in right ])
    return achievements


def getTeamPlayerAchievements(player, reusable):
    playerAchievements = player.getAchievements()
    achievements = [ prepareAchievementData(item, PostbattleAchievementModel.ACHIEVEMENT_RIGHT_BLOCK, reusable) for item in playerAchievements ]
    return achievements


def prepareAchievementData(item, groupID, reusable):
    achievement = item[0]
    achievementName = achievement.getRecordName()[1]
    if achievementName == PostbattleAchievementModel.MARK_OF_MASTERY:
        groupID = MARK_OF_MASTERY
    elif achievementName == PostbattleAchievementModel.MARK_ON_GUN:
        groupID = MARK_ON_GUN
    return _AchievementData(name=achievement.getName(), isEpic=achievement.hasRibbon(), iconName=achievement.getIconName(), groupID=groupID, tooltipType=getAchievementTooltipType(achievementName), tooltipArgs=getAchievementTooltipArgs(achievement, reusable))


def getAchievementTooltipType(achievementName):
    if achievementName == MARK_OF_MASTERY:
        return TOOLTIPS_CONSTANTS.MARK_OF_MASTERY
    return TOOLTIPS_CONSTANTS.BATTLE_STATS_MARKS_ON_GUN_ACHIEVEMENT if achievementName == MARK_ON_GUN else TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS


def getAchievementTooltipArgs(achievement, reusable):
    achievementTooltipArgs = [achievement.getBlock(),
     achievement.getName(),
     achievement.getValue() if achievement.getType() != ACHIEVEMENT_TYPE.SERIES else 0,
     getAchievementCustomData(achievement),
     getVehicleLevel(reusable),
     reusable.bonusType]
    return json.dumps(achievementTooltipArgs)
