# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/winback_mode_selector_item.py
from account_helpers.AccountSettings import Winback, AccountSettings
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.impl.gen import R
from gui.impl.lobby.mode_selector.items.random_mode_selector_item import RandomModeSelectorItem
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import g_eventBus
from gui.shared.events import ModeSelectorPopoverEvent
from gui.winback.winback_helpers import getWinbackSetting

class WinbackModeSelectorItem(RandomModeSelectorItem):

    @property
    def modeName(self):
        return PREBATTLE_ACTION_NAME.RANDOM

    def isSelected(self):
        return battle_selector_items.getItems().isSelected(PREBATTLE_ACTION_NAME.WINBACK)

    def getViewModel(self):
        return self.viewModel

    def _onInitializing(self):
        super(WinbackModeSelectorItem, self)._onInitializing()
        AccountSettings.onSettingsChanging += self.__onAccountSettingsChanging
        g_eventBus.addListener(ModeSelectorPopoverEvent.NAME, self.__onModeSelectorPopoverEvent)
        self.__fillCardModel()

    def _onDisposing(self):
        AccountSettings.onSettingsChanging -= self.__onAccountSettingsChanging
        g_eventBus.removeListener(ModeSelectorPopoverEvent.NAME, self.__onModeSelectorPopoverEvent)
        super(WinbackModeSelectorItem, self)._onDisposing()

    def _isInfoIconVisible(self):
        return False

    def __onAccountSettingsChanging(self, key, _):
        if key == Winback.WINBACK_SETTINGS:
            self.onCardChange()

    def __onModeSelectorPopoverEvent(self, event):
        self.viewModel.setIsSettingsActive(event.ctx['active'])

    @replaceNoneKwargsModel
    def __fillCardModel(self, model=None):
        isBattleSelectorSettingsBulletShown = getWinbackSetting(Winback.BATTLE_SELECTOR_SETTINGS_BULLET_SHOWN)
        model.setSettingsPopoverID(R.views.lobby.winback.popovers.WinbackLeaveModePopoverView())
        model.setWithSettingsNotification(not isBattleSelectorSettingsBulletShown)
        model.setIsSettingsActive(False)
