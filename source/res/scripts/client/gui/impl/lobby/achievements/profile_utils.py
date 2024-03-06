# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/achievements/profile_utils.py
from adisp import adisp_process
from dossiers2.ui.achievements import ACHIEVEMENT_SECTION, ACHIEVEMENT_SECTIONS_INDICES
from gui.impl import backport
from gui.impl.backport import getIntegralFormat
from gui.impl.gen.view_models.constants.date_time_formats import DateTimeFormatsEnum
from gui.shared.formatters import text_styles
from gui.shared.formatters.date_time import getRegionalDateTime
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isLayoutEnabled(lobbyContext=None):
    return lobbyContext.getServerSettings().getAchievements20GeneralConfig().isLayoutEnabled()


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isSummaryEnabled(lobbyContext=None):
    return lobbyContext.getServerSettings().getAchievements20GeneralConfig().isSummaryEnabled()


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isWTREnabled(lobbyContext=None):
    return lobbyContext.getServerSettings().getAchievements20GeneralConfig().isWTREnabled()


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getStagesOfWTR(lobbyContext=None):
    return lobbyContext.getServerSettings().getAchievements20GeneralConfig().getStagesOfWTR()


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getLayoutLength(lobbyContext=None):
    return lobbyContext.getServerSettings().getAchievements20GeneralConfig().getLayoutLength()


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def isEditingEnabled(itemsCache=None, lobbyContext=None):
    achievements20GeneralConfig = lobbyContext.getServerSettings().getAchievements20GeneralConfig()
    mainRules = achievements20GeneralConfig.getAutoGeneratingMainRules()
    extraRules = achievements20GeneralConfig.getAutoGeneratingExtraRules()
    totalCount = 0
    countAchievementsOnRibbon = 0
    layoutLength = getLayoutLength()
    achievements = itemsCache.items.getAccountDossier().getTotalStats().getAchievements(isInDossier=True, showHidden=False)
    for sectionName, maxAchievements in mainRules:
        countOfAchievements = len(achievements[ACHIEVEMENT_SECTIONS_INDICES[sectionName]])
        totalCount += countOfAchievements
        countAchievementsOnRibbon += maxAchievements if countOfAchievements >= maxAchievements else countOfAchievements
        if countAchievementsOnRibbon >= layoutLength and totalCount > layoutLength:
            return True

    for sectionName in extraRules:
        countOfAchievements = len(achievements[ACHIEVEMENT_SECTIONS_INDICES[sectionName]])
        totalCount += countOfAchievements
        countAchievementsOnRibbon += countOfAchievements
        if countAchievementsOnRibbon >= layoutLength and totalCount > layoutLength:
            return True

    return False


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getRating(itemsCache=None, userId=None):
    if isWTREnabled():
        return itemsCache.items.getWTR(userId)
    elif userId is not None:
        result = dict()
        _receiveRating(itemsCache, userId, result)
        return result.get('globalRating', 0)
    else:
        return itemsCache.items.stats.globalRating


@adisp_process
def _receiveRating(itemsCache, userId, result):
    req = itemsCache.items.dossiers.getUserDossierRequester(int(userId))
    result['globalRating'] = yield req.getGlobalRating()


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getAllAchievements(itemsCache=None):
    achievements = itemsCache.items.getAccountDossier().getTotalStats().getAchievements(isInDossier=True, showHidden=False)
    total = 0
    unique = 0
    for section in achievements:
        for achievement in section:
            unique += 1
            if achievement.isDone():
                total += 1
            if achievement.getValue() > 0:
                if achievement.getSection() == ACHIEVEMENT_SECTION.CLASS:
                    total += 1
                else:
                    total += achievement.getValue()

    return (total, unique)


def getProfileCommonInfo(dossier):
    lastBattleDate = None
    lastBattleTime = None
    if dossier['total']['lastBattleTime']:
        lbt = dossier['total']['lastBattleTime']
        lastBattleDate = getRegionalDateTime(lbt, DateTimeFormatsEnum.FULLDATE)
        lastBattleTime = getRegionalDateTime(lbt, DateTimeFormatsEnum.SHORTTIME)
    return {'registrationDate': '%s' % getRegionalDateTime(dossier['total']['creationTime'], DateTimeFormatsEnum.FULLDATE),
     'lastBattleDate': lastBattleDate,
     'lastBattleTime': lastBattleTime}


def getNormalizedValue(targetValue):
    return targetValue if targetValue is not None else 0


def getFormattedValue(targetValue):
    return getIntegralFormat(getNormalizedValue(targetValue))


def formatPercent(value):
    value = text_styles.concatStylesWithSpace(backport.getNiceNumberFormat(value), '%')
    return value
