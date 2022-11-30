# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/reward_kit_entry_point.py
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.reward_kit_entry_point_model import RewardKitEntryPointModel
from gui.impl.lobby.loot_box.loot_box_helper import showRestrictedSysMessage
from gui.impl.lobby.new_year.tooltips.ny_reward_kits_unavailable_tooltip import NyRewardKitsUnavailableTooltip
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showLootBoxEntry, showLootBoxBuyWindow
from gui.shared.events import GameEvent
from helpers import dependency
from ny_common.settings import NYLootBoxConsts
from realm import CURRENT_REALM
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.new_year.new_year_helper import getRewardKitsCount

class RewardKitEntrancePointInjectWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return RewardKitEntrancePointWidget()


class RewardKitEntrancePointWidget(ViewImpl):
    settingsCore = dependency.descriptor(ISettingsCore)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ('__isRewardKitsEnabled',)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.loot_box.RewardKitEntryView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = RewardKitEntryPointModel()
        super(RewardKitEntrancePointWidget, self).__init__(settings)
        self.__isRewardKitsEnabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()

    @property
    def viewModel(self):
        return super(RewardKitEntrancePointWidget, self).getViewModel()

    def _initialize(self):
        super(RewardKitEntrancePointWidget, self)._initialize()
        g_eventBus.handleEvent(GameEvent(GameEvent.CLOSE_LOOT_BOX_WINDOWS))
        self.viewModel.onOpenKit += self._onOpenKit
        self.itemsCache.onSyncCompleted += self.__onUpdate
        self.settingsCore.onSettingsChanged += self.__onUpdate
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.__update()

    def _finalize(self):
        self.viewModel.onOpenKit -= self._onOpenKit
        self.itemsCache.onSyncCompleted -= self.__onUpdate
        self.settingsCore.onSettingsChanged -= self.__onUpdate
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.settingsCore.serverSettings.settingsCache.onSyncCompleted -= self.__onSyncCompleted
        super(RewardKitEntrancePointWidget, self)._finalize()

    def createToolTipContent(self, event, contentID):
        return NyRewardKitsUnavailableTooltip() if event.contentID == R.views.lobby.new_year.tooltips.NyRewardKitsUnavailableTooltip() else super(RewardKitEntrancePointWidget, self).createToolTipContent(event, contentID)

    def _onOpenKit(self):
        if getRewardKitsCount() > 0:
            showLootBoxEntry()
        else:
            showLootBoxBuyWindow()

    def __onUpdate(self, *_):
        self.__update()

    def __update(self):
        kitsCount = getRewardKitsCount()
        if not self.settingsCore.serverSettings.settingsCache.isSynced():
            self.settingsCore.serverSettings.settingsCache.onSyncCompleted += self.__onSyncCompleted
            return
        kitViewed = self.settingsCore.serverSettings.getSectionSettings(SETTINGS_SECTIONS.LOOT_BOX_VIEWED, 'count', 0)
        hasNew = kitsCount > kitViewed
        shopConfig = self.lobbyContext.getServerSettings().getLootBoxShop()
        source = shopConfig.get(NYLootBoxConsts.SOURCE, NYLootBoxConsts.EXTERNAL)
        with self.viewModel.transaction() as model:
            model.setKitsCount(kitsCount)
            model.setHasNew(hasNew)
            model.setIsDisabled(not self.__isRewardKitsEnabled)
            model.setIsExternal(source == NYLootBoxConsts.EXTERNAL)
            model.setRealm(CURRENT_REALM)

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff:
            self.__update()
        enabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()
        if enabled != self.__isRewardKitsEnabled:
            if not enabled:
                showRestrictedSysMessage()
            self.__isRewardKitsEnabled = enabled
            self.viewModel.setIsDisabled(self.__isRewardKitsEnabled)

    def __onSyncCompleted(self, *_):
        self.settingsCore.serverSettings.settingsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__update()
