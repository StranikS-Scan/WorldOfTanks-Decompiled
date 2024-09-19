# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/comp7_gui_helpers.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR, COMP7_UI_SECTION, COMP7_LAST_SEASON
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from comp7_common import seasonNameBySeasonNumber
from comp7_common import seasonPointsCodeBySeasonNumber
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache

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
    return _needToShowComp7Intro() and not _hasParticipantToken()


def isComp7WhatsNewShouldBeShown():
    return _needToShowComp7Intro() and _hasParticipantToken()


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def updateComp7LastSeason(comp7Controller=None):
    if not comp7Controller.hasActiveSeason():
        return
    settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
    season = comp7Controller.getCurrentSeason()
    settings[COMP7_LAST_SEASON] = seasonNameBySeasonNumber(season.getNumber())
    AccountSettings.setUIFlag(COMP7_UI_SECTION, settings)


@dependency.replace_none_kwargs(settingsCore=ISettingsCore)
def isViewShown(key, settingsCore=None):
    section = settingsCore.serverSettings.getSection(section=GUI_START_BEHAVIOR, defaults=AccountSettings.getFilterDefault(GUI_START_BEHAVIOR))
    return section.get(key)


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def _needToShowComp7Intro(comp7Controller=None):
    if not comp7Controller.hasActiveSeason():
        return False
    settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
    season = comp7Controller.getCurrentSeason()
    return settings.get(COMP7_LAST_SEASON) != seasonNameBySeasonNumber(season.getNumber())


@dependency.replace_none_kwargs(comp7Controller=IComp7Controller, itemsCache=IItemsCache)
def _hasParticipantToken(comp7Controller=None, itemsCache=None):
    for participantToken in comp7Controller.getModeSettings().participantTokens:
        tokenInfo = itemsCache.items.tokens.getTokens().get(participantToken)
        if tokenInfo is not None:
            _, count = tokenInfo
            if count > 0:
                return True

    return False
