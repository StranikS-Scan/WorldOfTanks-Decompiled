# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/popovers/random_battle_popover.py
from collections import OrderedDict
from account_helpers.settings_core.settings_constants import GAME
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.popovers.random_battle_popover_item_model import RandomBattlePopoverItemModel
from gui.impl.gen.view_models.views.lobby.mode_selector.popovers.random_battle_popover_model import RandomBattlePopoverModel
from gui.impl.lobby.mode_selector.tooltips.mode_selector_alert_tooltip import AlertTooltip
from gui.impl.pub.view_impl import PopOverViewImpl
from gui.shared import g_eventBus
from gui.shared.events import ModeSelectorPopoverEvent
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
_GAMEPLAY_STANDARD = 'gameplay_standard'
_subLocaleBySettingID = OrderedDict()
_subLocaleBySettingID[_GAMEPLAY_STANDARD] = 'default'
_subLocaleBySettingID[GAME.GAMEPLAY_DOMINATION] = 'domination'
_subLocaleBySettingID[GAME.GAMEPLAY_ASSAULT] = 'assault'
_subLocaleBySettingID[GAME.GAMEPLAY_EPIC_STANDARD] = 'epicStandard'
_subLocaleBySettingID[GAME.GAMEPLAY_DEV_MAPS] = 'devMaps'

class RandomBattlePopover(PopOverViewImpl):
    __slots__ = ('__initialItems', '__currentItems')
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.lobby.mode_selector.popovers.RandomBattlePopover(), model=RandomBattlePopoverModel())
        self.__initialItems = dict()
        self.__currentItems = dict()
        super(RandomBattlePopover, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return AlertTooltip(event.getArgument('header', ''), event.getArgument('body', ''), event.getArgument('alert', '')) if contentID == R.views.lobby.mode_selector.tooltips.AlertTooltip() else None

    def _onLoading(self, *args, **kwargs):
        self.viewModel.onItemChanged += self._itemChangeHandler
        settings = [GAME.GAMEPLAY_DOMINATION,
         GAME.GAMEPLAY_ASSAULT,
         GAME.GAMEPLAY_EPIC_STANDARD,
         GAME.GAMEPLAY_DEV_MAPS]
        for setting in settings:
            self.__initialItems[setting] = self.__currentItems[setting] = self.settingsCore.getSetting(setting)

        self._update()

    def _initialize(self, *args):
        super(RandomBattlePopover, self)._initialize()
        g_eventBus.handleEvent(ModeSelectorPopoverEvent(ModeSelectorPopoverEvent.NAME, ctx={'active': True}))

    def _finalize(self):
        g_eventBus.handleEvent(ModeSelectorPopoverEvent(ModeSelectorPopoverEvent.NAME, ctx={'active': False}))
        self.viewModel.onItemChanged -= self._itemChangeHandler
        diff = dict(set(self.__currentItems.items()) - set(self.__initialItems.items()))
        if diff:
            self.settingsCore.applySettings(diff)
            self.settingsCore.applyStorages(restartApproved=False)
            self.settingsCore.clearStorages()
        super(RandomBattlePopover, self)._finalize()

    def _update(self):
        titlesR = R.strings.mode_selector.popover
        tooltipsR = R.strings.tooltips.mode_selector.popover
        with self.viewModel.transaction() as model:
            settingsList = model.getSettingsList()
            settingsList.clear()
            for itemType, itemLocale in _subLocaleBySettingID.iteritems():
                if itemType != GAME.GAMEPLAY_DEV_MAPS or self.lobbyContext.getServerSettings().isMapsInDevelopmentEnabled():
                    settingsList.addViewModel(self._createItem(itemType, titlesR.dyn(itemLocale)(), tooltipsR.dyn(itemLocale), enabled=itemType != _GAMEPLAY_STANDARD))

            settingsList.invalidate()

    def _createItem(self, setting, title, tooltip, enabled):
        alert = backport.text(tooltip.attention()) if tooltip.dyn('attention') else ''
        item = RandomBattlePopoverItemModel()
        item.setTitle(title)
        item.setTooltipHeader(tooltip.header())
        item.setTooltipBody(tooltip.body())
        item.setTooltipAlert(alert)
        item.setType(setting)
        item.setIsChecked(self.__currentItems.get(setting, True))
        item.setIsEnabled(enabled)
        return item

    def _itemChangeHandler(self, event):
        setting = str(event.get('type'))
        newValue = not self.__currentItems[setting]
        self.__currentItems[setting] = newValue
        self._update()
