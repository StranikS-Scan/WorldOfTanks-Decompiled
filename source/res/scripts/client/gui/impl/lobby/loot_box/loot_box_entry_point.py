# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_entry_point.py
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_entry_point_model import LootBoxEntryPointModel
from gui.impl.lobby.loot_box.loot_box_helper import showRestrictedSysMessage
from gui.impl.lobby.tooltips.loot_box_entry_tooltip_content import LootBoxEntryTooltipContent
from gui.impl.lobby.loot_box.loot_box_popover_content import LootBoxPopoverContent
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showLootBoxEntry
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.new_year.new_year_helper import getNYLootboxCount

class LootboxesEntrancePointInjectWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return LootboxesEntrancePointWidget()


class LootboxesEntrancePointWidget(ViewImpl):
    settingsCore = dependency.descriptor(ISettingsCore)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ('__isLootBoxesEnabled',)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.loot_box.views.loot_box_entry_point_view.LootBoxEntryPointView())
        settings.flags = ViewFlags.VIEW
        settings.model = LootBoxEntryPointModel()
        super(LootboxesEntrancePointWidget, self).__init__(settings)
        self.__isLootBoxesEnabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()

    @property
    def viewModel(self):
        return super(LootboxesEntrancePointWidget, self).getViewModel()

    def createPopOverContent(self, event):
        return LootBoxPopoverContent()

    def createToolTipContent(self, event, contentID):
        return LootBoxEntryTooltipContent() if event.contentID == R.views.lobby.tooltips.loot_box_entry_tooltip_content.LootBoxEntryTooltipContent() else None

    def _initialize(self):
        super(LootboxesEntrancePointWidget, self)._initialize()
        self.viewModel.onWidgetClick += self._onWidgetClick
        self.itemsCache.onSyncCompleted += self.__onUpdate
        self.settingsCore.onSettingsChanged += self.__onUpdate
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.__update()

    def _finalize(self):
        self.viewModel.onWidgetClick -= self._onWidgetClick
        self.itemsCache.onSyncCompleted -= self.__onUpdate
        self.settingsCore.onSettingsChanged -= self.__onUpdate
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(LootboxesEntrancePointWidget, self)._finalize()

    def _onWidgetClick(self, _=None):
        showLootBoxEntry()

    def __onUpdate(self, *_):
        self.__update()

    def __update(self):
        lootboxesCount = getNYLootboxCount()
        self.viewModel.setBoxesCount(lootboxesCount)
        lootBoxViewed = self.settingsCore.serverSettings.getSectionSettings(SETTINGS_SECTIONS.LOOT_BOX_VIEWED, 'count', 0)
        self.viewModel.setHasNew(lootboxesCount > lootBoxViewed)

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff:
            self.__update()
        enabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()
        if enabled != self.__isLootBoxesEnabled:
            if not enabled:
                showRestrictedSysMessage()
            self.__isLootBoxesEnabled = enabled
