# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/winback_mode_selector_item.py
from account_helpers.AccountSettings import Winback, AccountSettings
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.impl.lobby.mode_selector.items.random_mode_selector_item import RandomModeSelectorItem
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.winback.winback_helpers import getWinbackSetting

class WinbackModeSelectorItem(RandomModeSelectorItem):

    @property
    def modeName(self):
        return PREBATTLE_ACTION_NAME.RANDOM

    def isSelected(self):
        return battle_selector_items.getItems().isSelected(PREBATTLE_ACTION_NAME.WINBACK)

    def _onInitializing(self):
        super(WinbackModeSelectorItem, self)._onInitializing()
        AccountSettings.onSettingsChanging += self.__onAccountSettingsChanging
        self.__setSettingsBullet()

    def _onDisposing(self):
        AccountSettings.onSettingsChanging -= self.__onAccountSettingsChanging
        super(WinbackModeSelectorItem, self)._onDisposing()

    def _isInfoIconVisible(self):
        return False

    def __setSettingsBullet(self):
        isBattleSelectorSettingsBulletShown = getWinbackSetting(Winback.BATTLE_SELECTOR_SETTINGS_BULLET_SHOWN)
        self.viewModel.setWithSettingsNotification(not isBattleSelectorSettingsBulletShown)

    def __onAccountSettingsChanging(self, key, _):
        if key == Winback.WINBACK_SETTINGS:
            self.onCardChange()
