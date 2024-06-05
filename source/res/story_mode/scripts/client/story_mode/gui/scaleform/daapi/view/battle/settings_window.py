# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/settings_window.py
from account_helpers.settings_core.settings_constants import SETTINGS_GROUP
from gui.Scaleform.daapi.view.common.settings import SettingsWindow
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.event_dispatcher import SettingsTabIndex
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from story_mode.uilogging.story_mode.consts import LogWindows, LogButtons
from story_mode.uilogging.story_mode.loggers import WindowLogger

class OnboardingSettingsWindow(SettingsWindow):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _TAB_NAME_TO_INDEX = {SETTINGS_GROUP.GAME_SETTINGS: SettingsTabIndex.GAME,
     SETTINGS_GROUP.GRAPHICS_SETTINGS: SettingsTabIndex.GRAPHICS,
     SETTINGS_GROUP.SOUND_SETTINGS: SettingsTabIndex.SOUND,
     SETTINGS_GROUP.CONTROLS_SETTINGS: SettingsTabIndex.CONTROL,
     SETTINGS_GROUP.AIM_SETTINGS: SettingsTabIndex.AIM,
     SETTINGS_GROUP.MARKERS_SETTINGS: SettingsTabIndex.MARKERS,
     SETTINGS_GROUP.FEEDBACK_SETTINGS: SettingsTabIndex.FEEDBACK}

    def __init__(self):
        super(OnboardingSettingsWindow, self).__init__(ctx={'redefinedKeyMode': True,
         'isBattleSettings': True,
         'tabIndex': self.sessionProvider.dynamic.overrideSettingsController.defaultTab})
        self._uiLogger = WindowLogger(LogWindows.SETTINGS_MENU)

    def as_setCountersDataS(self, countersData):
        disabledTabs = self.sessionProvider.dynamic.overrideSettingsController.disabledTabs
        countersData = [ item for item in countersData if self._TAB_NAME_TO_INDEX[item['tabId']] not in disabledTabs ]
        super(OnboardingSettingsWindow, self).as_setCountersDataS(countersData)

    def applySettings(self, settings, isCloseWnd):
        self._uiLogger.logClick(LogButtons.OK if isCloseWnd else LogButtons.APPLY)
        super(OnboardingSettingsWindow, self).applySettings(settings, isCloseWnd)

    def onTabSelected(self, tabId):
        self._uiLogger.logClick(button=LogButtons.TAB, state=str(tabId))
        super(OnboardingSettingsWindow, self).onTabSelected(tabId)

    def _populate(self):
        super(OnboardingSettingsWindow, self)._populate()
        self.as_setDisabledTabsOverlayS(self.sessionProvider.dynamic.overrideSettingsController.disabledTabs, backport.text(R.strings.sm_battle.settings.disabledTabsOverlay()))
        self._uiLogger.logOpen()

    def _dispose(self):
        self._uiLogger.logClose()
        super(OnboardingSettingsWindow, self)._dispose()
