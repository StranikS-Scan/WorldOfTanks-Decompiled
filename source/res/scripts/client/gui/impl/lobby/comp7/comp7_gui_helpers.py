# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_gui_helpers.py
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from comp7_common import seasonPointsCodeBySeasonNumber
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IComp7Controller

@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def isSeasonStasticsShouldBeShown(comp7Controller=None):
    currentSeason = comp7Controller.getCurrentSeason()
    if currentSeason:
        return False
    previousSeason = comp7Controller.getPreviousSeason()
    if not previousSeason:
        return False
    if isViewShown(GuiSettingsBehavior.COMP7_SEASON_STATISTICS_SHOWN):
        return False
    seasonPointsCode = seasonPointsCodeBySeasonNumber(previousSeason.getNumber())
    receivedSeasonPoints = comp7Controller.getReceivedSeasonPoints().get(seasonPointsCode)
    return False if not receivedSeasonPoints else True


def isComp7OnboardingShouldBeShown():
    return not isViewShown(GuiSettingsBehavior.COMP7_INTRO_SHOWN)


def isComp7WhatsNewShouldBeShown():
    return not isViewShown(GuiSettingsBehavior.COMP7_WHATS_NEW_SHOWN)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def isViewShown(key, settingsCore=None):
    section = settingsCore.serverSettings.getSection(section=GUI_START_BEHAVIOR, defaults=AccountSettings.getFilterDefault(GUI_START_BEHAVIOR))
    return section.get(key)
