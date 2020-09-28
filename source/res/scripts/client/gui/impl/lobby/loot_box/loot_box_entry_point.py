# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_entry_point.py
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_entry_point_model import LootBoxEntryPointModel
from gui.impl.lobby.wt_event.tooltips.wt_event_lootbox_tooltip_view import WtEventLootboxTooltipView
from gui.impl.lobby.loot_box.loot_box_popover_content import LootBoxPopoverContent
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IEventLootBoxesController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext

class LootboxesEntrancePointWidget(ViewImpl):
    settingsCore = dependency.descriptor(ISettingsCore)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    lootBoxesController = dependency.descriptor(IEventLootBoxesController)
    __slots__ = ('__isLootBoxesEnabled',)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.loot_box.views.loot_box_entry_point_view.LootBoxEntryPointView(), ViewFlags.COMPONENT, LootBoxEntryPointModel())
        super(LootboxesEntrancePointWidget, self).__init__(settings)
        self.__isLootBoxesEnabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()

    @property
    def viewModel(self):
        return super(LootboxesEntrancePointWidget, self).getViewModel()

    def createPopOverContent(self, event):
        return LootBoxPopoverContent()

    def createToolTipContent(self, event, contentID):
        return WtEventLootboxTooltipView() if contentID == R.views.lobby.wt_event.tooltips.WtEventLootboxTooltipView() else None

    def _initialize(self):
        super(LootboxesEntrancePointWidget, self)._initialize()
        self.lootBoxesController.onUpdated += self.__onUpdate
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.viewModel.onWidgetClick += self.__onWidgetClick
        self.__update()

    def _finalize(self):
        self.lootBoxesController.onUpdated -= self.__onUpdate
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.viewModel.onWidgetClick -= self.__onWidgetClick
        super(LootboxesEntrancePointWidget, self)._finalize()

    def __onUpdate(self, *_):
        self.__update()

    def __update(self):
        lootBoxesCount = self.lootBoxesController.getEventLootBoxesCount()
        lastViewed = self.lootBoxesController.getLastViewed()
        self.viewModel.setBoxesCount(lootBoxesCount)
        self.viewModel.setHasNew(lootBoxesCount > lastViewed)

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff:
            self.__update()
        self.__isLootBoxesEnabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()

    def __onWidgetClick(self):
        self.lootBoxesController.setLastViewed()
        self.viewModel.setHasNew(False)
