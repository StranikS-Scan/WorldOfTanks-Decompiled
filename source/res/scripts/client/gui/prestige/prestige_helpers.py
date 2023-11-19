# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prestige/prestige_helpers.py
import logging
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeLevelGrade
from gui.impl.pub.notification_commands import WindowNotificationCommand
from helpers import dependency
from prestige_system.prestige_common import PrestigeGrade
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import INotificationWindowController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Tuple, List
    from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeEmblemModel
_MIN_SUB_GRADE_NUMBER = 1
_MAX_SUB_GRADE_NUMBER = 4
_INVALID_GRADE_NUMBER = -1
_COMPLEX_GRADES = (PrestigeLevelGrade.IRON,
 PrestigeLevelGrade.BRONZE,
 PrestigeLevelGrade.SILVER,
 PrestigeLevelGrade.GOLD,
 PrestigeLevelGrade.ENAMEL)
_SIMPLE_GRADES = (PrestigeLevelGrade.UNDEFINED, PrestigeLevelGrade.MAXIMUM)
_gradeIDtoGradeUIMap = dict(((index, value) for index, value in enumerate([ (s, g) for s in _COMPLEX_GRADES for g in range(_MIN_SUB_GRADE_NUMBER, _MAX_SUB_GRADE_NUMBER + 1) ] + [(PrestigeLevelGrade.MAXIMUM, _INVALID_GRADE_NUMBER)], 1)))
MAX_GRADE_ID = max(_gradeIDtoGradeUIMap.keys())
DEFAULT_PRESTIGE = (0, 0)

def mapGradeIDToUI(gradeID):
    return _gradeIDtoGradeUIMap.get(gradeID, (PrestigeLevelGrade.UNDEFINED, _INVALID_GRADE_NUMBER))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getVehiclePrestige(vehCD, databaseID=None, itemsCache=None):
    accDossier = itemsCache.items.getAccountDossier(databaseID=databaseID)
    return accDossier.getPrestigeStats().getVehicles().get(vehCD, DEFAULT_PRESTIGE)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getCurrentProgress(vehCD, currentLevel, remainingPts, lobbyContext=None):
    points = lobbyContext.getServerSettings().prestigeConfig.getVehiclePoints(vehCD)
    if not points:
        return (-1, -1)
    pointsLength = len(points)
    if currentLevel >= pointsLength:
        return (1, 1)
    if currentLevel < 1:
        _logger.error('Points for vehicle (intCD = %s) not have this level = %s. Points = %s', vehCD, currentLevel, points)
        return (-1, -1)
    nextLevelPts = points[currentLevel]
    currentXP = prestigePointsToXP(remainingPts, lobbyContext=lobbyContext)
    nextLvlXP = prestigePointsToXP(nextLevelPts, lobbyContext=lobbyContext)
    if currentXP == nextLvlXP:
        currentXP -= 1
    return (currentXP, nextLvlXP)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def prestigePointsToXP(points, lobbyContext=None):
    prestigeCoefficient = lobbyContext.getServerSettings().prestigeConfig.prestigeCoefficient
    if prestigeCoefficient == 0:
        _logger.warning('Prestige coefficient is 0. Check configs.')
        return points
    return int(round(points / prestigeCoefficient))


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, itemsCache=IItemsCache)
def hasVehiclePrestige(vehCD, checkElite=False, lobbyContext=None, itemsCache=None):
    config = lobbyContext.getServerSettings().prestigeConfig
    if not config.isEnabled:
        return False
    if not config.getVehiclePoints(vehCD):
        return False
    if checkElite:
        vehicle = itemsCache.items.getItemByCD(vehCD)
        if not vehicle.isElite:
            return False
    return True


def getCurrentGrade(currentLvl, vehCD):
    gradeID = 0
    for grade in getSortedGrades(vehCD):
        if currentLvl < grade.level:
            break
        gradeID = grade.prestigeMarkID

    return gradeID


def getNextGradeLevel(currentLevel, vehCD):
    nextLevel = currentLevel
    for grade in getSortedGrades(vehCD):
        nextLevel = grade.level
        if currentLevel < grade.level:
            break

    return nextLevel


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getSortedGrades(vehCD, onlyMain=False, lobbyContext=None):
    config = lobbyContext.getServerSettings().prestigeConfig
    grades = config.getSortedMainGrades() if onlyMain else config.getSortedGrades()
    vehiclePoints = config.getVehiclePoints(vehCD)
    if not vehiclePoints:
        return []
    maxLevel = len(vehiclePoints)
    if maxLevel < config.defaultMaxLevel:
        grades = [ grade for grade in grades if grade.level < maxLevel ]
    return grades + [PrestigeGrade(level=maxLevel, prestigeMarkID=MAX_GRADE_ID, main=True)]


def fillPrestigeEmblemModel(model, level, vehCD):
    model.setLevel(level)
    gradeType, grade = mapGradeIDToUI(getCurrentGrade(level, vehCD))
    model.setType(gradeType)
    model.setGrade(grade)


def needShowPrestigeRewardWindow(vehCD, oldLvl, newLvl):
    for grade in getSortedGrades(vehCD, onlyMain=True):
        if oldLvl < grade.level <= newLvl:
            return True

    return False


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def showPrestigeVehicleStats(vehIntCD, lobbyContext=None):
    config = lobbyContext.getServerSettings().prestigeConfig
    if not isOnboardingViewed() and config.isEnabled:
        showPrestigeOnboardingWindow()
        return
    from gui.shared.event_dispatcher import showVehicleStats
    showVehicleStats(vehIntCD, selectedAlias=VIEW_ALIAS.PROFILE_TECHNIQUE_PAGE, initVehicleSorting={'selectedColumnSorting': 'descending',
     'selectedColumnStr': 'prestigeLevel'})


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showPrestigeRewardWindow(vehIntCD, level, notificationMgr=None):
    from gui.impl.lobby.prestige.prestige_reward_view import PrestigeRewardViewWindow
    window = PrestigeRewardViewWindow(vehIntCD, level)
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showPrestigeOnboardingWindow(notificationMgr=None):
    from gui.impl.lobby.prestige.global_onboarding_view import GlobalOnboardingWindow
    window = GlobalOnboardingWindow()
    notificationMgr.append(WindowNotificationCommand(window))


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def isOnboardingViewed(settingsCore=None):
    defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
    settings = settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
    return settings.get(GuiSettingsBehavior.IS_PRESTIGE_ONBOARDING_VIEWED, False)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def setOnboardingViewed(settingsCore=None):
    defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
    settings = settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
    settings[GuiSettingsBehavior.IS_PRESTIGE_ONBOARDING_VIEWED] = True
    settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, settings)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def isFirstEntryNotificationShown(settingsCore=None):
    defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
    settings = settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
    return settings.get(GuiSettingsBehavior.PRESTIGE_FIRST_ENTRY_NOTIFICATION_SHOWN, False)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def setFirstEntryNotificationShown(settingsCore=None):
    defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
    settings = settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
    settings[GuiSettingsBehavior.PRESTIGE_FIRST_ENTRY_NOTIFICATION_SHOWN] = True
    settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, settings)
