# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/achievements/achievements_helper.py
from dossiers2.custom.records import RECORD_DB_IDS, DB_ID_TO_RECORD
from dossiers2.ui.achievements import ACHIEVEMENT_TYPE
from gui.impl.gen.view_models.views.lobby.achievements.achievement_model import AchievementType, AchievementModel, CounterType
from gui.impl.gen.view_models.views.lobby.achievements.views.achievement_section_model import AchievementSectionModel
from gui.shared.gui_items.dossier.achievements.abstract import isRareAchievement
COUNTER_TYPE_MAP = {ACHIEVEMENT_TYPE.CLASS: CounterType.STAGES,
 ACHIEVEMENT_TYPE.SERIES: CounterType.SERIES,
 ACHIEVEMENT_TYPE.CUSTOM: CounterType.NONE,
 ACHIEVEMENT_TYPE.REPEATABLE: CounterType.SIMPLE}
_ACHIEVEMENT_TYPE_MAP = {ACHIEVEMENT_TYPE.REPEATABLE: AchievementType.REPEATABLE,
 ACHIEVEMENT_TYPE.CLASS: AchievementType.CLASS,
 ACHIEVEMENT_TYPE.CUSTOM: AchievementType.CUSTOM,
 ACHIEVEMENT_TYPE.SERIES: AchievementType.SERIES,
 ACHIEVEMENT_TYPE.SINGLE: AchievementType.SINGLE}

def fillAchievementSectionModel(section):
    achievementSectionModel = AchievementSectionModel()
    achievementsModel = achievementSectionModel.getAchievements()
    for achievement in section:
        achievementModel = fillAchievementModel(achievement)
        achievementsModel.addViewModel(achievementModel)

    return achievementSectionModel


def fillAchievementModel(achievement):
    isRare = isRareAchievement(achievement)
    aType = AchievementType.RARE if isRare else _ACHIEVEMENT_TYPE_MAP.get(achievement.getType(), '')
    achievementModel = AchievementModel()
    achievementModel.setName(achievement.getName())
    achievementModel.setResourceName(achievement.getResourceName())
    achievementModel.setBlock(achievement.getBlock())
    achievementModel.setType(aType)
    achievementModel.setCounterType(COUNTER_TYPE_MAP.get(aType.value, CounterType.NONE))
    achievementModel.setValue(achievement.getValue())
    if isRare:
        achievementModel.setRareIconId(achievement.requestImagePath())
        achievementModel.setRareBigIconId(achievement.requestBigImagePath())
    return achievementModel


def convertAchievementsToDbIds(achivements):
    achievementsIdx = []
    for achievement in achivements:
        if isRareAchievement(achievement):
            achievementsIdx.append(-achievement.getRareID())
        achievementsIdx.append(RECORD_DB_IDS[achievement.getBlock(), achievement.getName()])

    return achievementsIdx


def convertDbIdsToAchievements(layout, dossier=None):
    achievements = []
    for achievementID in layout:
        if achievementID > 0:
            achievements.append(dossier.getTotalStats().getAchievement(DB_ID_TO_RECORD[achievementID]))
        achievements.append(dossier.getTotalStats().getAchievement(('rareAchievements', -achievementID)))

    return achievements
