# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/achievements.py
from collections import namedtuple
from itertools import chain
import typing
from frameworks.wulf import Array
from gui.battle_results.br_helper import getShortVehicleInfo, BattleResultData
from gui.battle_results.reusable import ReusableInfo
from gui.battle_results.reusable.shared import makeAchievement, makeMarkOfMasteryFromPersonal, VehicleSummarizeInfo
from gui.impl.gen.view_models.views.lobby.postbattle.achievement_model import AchievementModel
from gui.impl.gen.view_models.views.lobby.postbattle.rewards_model import RewardsModel
from gui.impl.gen.view_models.views.lobby.postbattle.player_details_model import PlayerDetailsModel
from gui.battle_results.br_helper import getAchievementCustomData, getArenaBonusType, getVehicleLevel
from dossiers2.ui.achievements import ACHIEVEMENT_TYPE, MARK_OF_MASTERY
from soft_exception import SoftException
_AchievementData = namedtuple('_AchievementData', ('achievementID', 'name', 'isEpic', 'iconName', 'groupID', 'isPersonal'))

def getAchievementTooltipArgs(achievID, achievName, isPersonal, battleResult):
    if not isPersonal:
        achievement = makeAchievement(achievID)
    else:
        vehicleInfo = getShortVehicleInfo(battleResult.reusable)
        intCD = vehicleInfo.intCD
        if achievName == MARK_OF_MASTERY:
            results = battleResult.rawResult['personal'][intCD]
            achievement = makeMarkOfMasteryFromPersonal(results)
            achievement.setPrevMarkOfMastery(results.get('prevMarkOfMastery', 0))
            achievement.setCompDescr(results.get('typeCompDescr'))
        else:
            achievement = makeAchievement(achievID, battleResult.rawResult['personal'][intCD])
    if achievement is None:
        SoftException('Achievement with id={} is incorrect'.format(achievID))
    return _packAchievementTooltipArgs(achievement, battleResult.reusable)


def setPersonalAchievements(model, reusable, result):
    left, right = reusable.personal.getAchievements(result['personal'])
    achievements = chain([ _processAchievement(item, AchievementModel.ACHIEVEMENT_LEFT_BLOCK) for item in left ], [ _processAchievement(item, AchievementModel.ACHIEVEMENT_RIGHT_BLOCK) for item in right ])
    _setAchievements(achievements, model)


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


def _fillCustomData(customData):
    customDataArray = Array()
    for value in customData:
        customDataArray.addNumber(value)

    return customDataArray


def _processAchievement(item, groupID):
    achievement = item.achievement
    achievementID = item.achievementID
    isPersonal = item.isPersonal
    return _AchievementData(achievementID=achievementID, name=achievement.getName(), isEpic=achievement.hasRibbon(), iconName=achievement.getIconName(), groupID=groupID, isPersonal=isPersonal)


def _packAchievementTooltipArgs(achievement, reusable):
    args = [achievement.getBlock(),
     achievement.getName(),
     achievement.getValue() if achievement.getType() != ACHIEVEMENT_TYPE.SERIES else 0,
     getAchievementCustomData(achievement),
     getVehicleLevel(reusable),
     getArenaBonusType(reusable)]
    return args
