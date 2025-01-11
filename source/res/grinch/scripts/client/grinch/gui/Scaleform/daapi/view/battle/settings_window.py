# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/battle/settings_window.py
from account_helpers.settings_core.settings_constants import SETTINGS_GROUP
from gui.Scaleform.daapi.view.common.settings import SettingsWindow
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.event_dispatcher import SettingsTabIndex
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class GrinchSettingsWindow(SettingsWindow):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _TAB_NAME_TO_INDEX = {SETTINGS_GROUP.GAME_SETTINGS: SettingsTabIndex.GAME,
     SETTINGS_GROUP.GRAPHICS_SETTINGS: SettingsTabIndex.GRAPHICS,
     SETTINGS_GROUP.SOUND_SETTINGS: SettingsTabIndex.SOUND,
     SETTINGS_GROUP.CONTROLS_SETTINGS: SettingsTabIndex.CONTROL,
     SETTINGS_GROUP.AIM_SETTINGS: SettingsTabIndex.AIM,
     SETTINGS_GROUP.MARKERS_SETTINGS: SettingsTabIndex.MARKERS,
     SETTINGS_GROUP.FEEDBACK_SETTINGS: SettingsTabIndex.FEEDBACK}

    def __init__(self):
        super(GrinchSettingsWindow, self).__init__(ctx={'redefinedKeyMode': True,
         'isBattleSettings': True,
         'tabIndex': self.__sessionProvider.dynamic.overrideSettingsController.defaultTab})

    def as_setCountersDataS(self, countersData):
        disabledTabs = self.__sessionProvider.dynamic.overrideSettingsController.disabledTabs
        countersData = [ item for item in countersData if self._TAB_NAME_TO_INDEX[item['tabId']] not in disabledTabs ]
        super(GrinchSettingsWindow, self).as_setCountersDataS(countersData)

    def _populate(self):
        super(GrinchSettingsWindow, self)._populate()
        self.as_setDisabledTabsOverlayS(self.__sessionProvider.dynamic.overrideSettingsController.disabledTabs, backport.text(R.strings.grinch.battle.settings.disabled()))
