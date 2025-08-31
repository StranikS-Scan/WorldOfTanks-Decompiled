# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/comp7/comp7_helpers.py
import logging
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_UI_SECTION, COMP7_FLAGS_VERSION, COMP7_WEEKLY_QUESTS_PAGE_TOKENS_COUNT, GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from gui import GUI_SETTINGS
from helpers.dependency import replace_none_kwargs
from skeletons.gui.game_control import IComp7Controller
from skeletons.account_helpers.settings_core import ISettingsCore
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import List
MAX_VERSION = 15

def getComp7DetailedHelpPages():
    return GUI_SETTINGS.comp7DetailedHelpPages.get('pages', [])


def getWhatsNewPages():
    return GUI_SETTINGS.whatsNewPageComp7Slides.get('pages', [])


def getIntroPages():
    return GUI_SETTINGS.IntroPagesComp7Slides.get('pages', [])


def getWhatsNewSeasonVehicles():
    return GUI_SETTINGS.whatsNewPageComp7Slides.get('seasonVehicles', [])


def getIntroVehicles():
    return GUI_SETTINGS.IntroPagesComp7Slides.get('seasonVehicles', [])


def getWhatsNewMapsAdded():
    return GUI_SETTINGS.whatsNewPageComp7Slides.get('newMaps', [])


def getWhatsNewMapsDeleted():
    return GUI_SETTINGS.whatsNewPageComp7Slides.get('deprecatedMaps', [])


def updateComp7Settings():
    _updateClientSettings()
    _updateServerSettings()


@replace_none_kwargs(comp7Controller=IComp7Controller)
def _updateClientSettings(comp7Controller=None):
    settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
    version = comp7Controller.getCurrentCycleID()
    if settings.get(COMP7_FLAGS_VERSION, 0) != version:
        settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
        settings[COMP7_WEEKLY_QUESTS_PAGE_TOKENS_COUNT] = 0
        AccountSettings.setUIFlag(COMP7_UI_SECTION, settings)
        settings[COMP7_FLAGS_VERSION] = version
        AccountSettings.setUIFlag(COMP7_UI_SECTION, settings)


@replace_none_kwargs(settingsCore=ISettingsCore, comp7Controller=IComp7Controller)
def _updateServerSettings(settingsCore=None, comp7Controller=None):
    version = comp7Controller.getCurrentCycleID()
    if version is None:
        return
    else:
        version = version % 100
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        data = settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        if data[GuiSettingsBehavior.COMP7_VERSION_FLAG] != version:
            data[GuiSettingsBehavior.COMP7_VERSION_FLAG] = version
            stateFlags = settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
            stateFlags[GuiSettingsBehavior.COMP7_WHATS_NEW_SHOWN] = False
            if version > MAX_VERSION:
                _logger.error('[COMP7] Version must be less 15')
            stateFlags[GuiSettingsBehavior.COMP7_VERSION_FLAG] = version
            settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)
        return
