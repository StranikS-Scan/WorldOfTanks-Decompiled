# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_loot_box_entry_point.py
from Event import Event
from constants import Configs
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_loot_box_entry_point_model import WtEventLootBoxEntryPointModel
from gui.impl.lobby.wt_event.tooltips.wt_event_lootboxes_tooltip_view import WtEventLootBoxesTooltipView
from gui.impl.lobby.wt_event.wt_event_inject_widget_view import WTEventInjectWidget
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.view.meta.WTEventBoxEntryPointWidgetMeta import WTEventBoxEntryPointWidgetMeta
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.event_dispatcher import showEventStorageWindow
from helpers import dependency, server_settings
from skeletons.gui.game_control import ILootBoxesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class WTEventLootBoxEntrancePointWidget(WTEventBoxEntryPointWidgetMeta, WTEventInjectWidget):

    def _makeInjectView(self):
        return LootboxesEntrancePointWidget()

    def getOnEscKeyDown(self):
        return self.getInjectView().onEscKeyDown


class LootboxesEntrancePointWidget(ViewImpl):
    __boxesCtrl = dependency.descriptor(ILootBoxesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ('onEscKeyDown',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wt_event.WTEventBoxEntryPoint(), flags=ViewFlags.COMPONENT, model=WtEventLootBoxEntryPointModel())
        settings.args = args
        settings.kwargs = kwargs
        self.onEscKeyDown = Event()
        super(LootboxesEntrancePointWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return WtEventLootBoxesTooltipView() if contentID == R.views.lobby.wt_event.tooltips.WtEventLootBoxesTooltipView() else super(LootboxesEntrancePointWidget, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(LootboxesEntrancePointWidget, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__updateViewModel()

    def _finalize(self):
        self.__removeListeners()
        super(LootboxesEntrancePointWidget, self)._finalize()

    def __addListeners(self):
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.viewModel.onWidgetClick += self.__onWidgetClick
        self.viewModel.onEscKeyDown += self.__onEscKeyDown

    def __removeListeners(self):
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.viewModel.onWidgetClick -= self.__onWidgetClick
        self.viewModel.onEscKeyDown -= self.__onEscKeyDown

    def __updateViewModel(self):
        hunterLootBoxes = self.__boxesCtrl.getLootBoxesCountByTypeForUI(EventLootBoxes.WT_HUNTER)
        bossLootBoxes = self.__boxesCtrl.getLootBoxesCountByTypeForUI(EventLootBoxes.WT_BOSS)
        hunterLastViewed, bossLastViewed = self.__boxesCtrl.getLastViewedCount()
        with self.viewModel.transaction() as model:
            model.setHunterLootBoxesCount(hunterLootBoxes)
            model.setBossLootBoxesCount(bossLootBoxes)
            model.setHunterHasNew(hunterLootBoxes > hunterLastViewed)
            model.setBossHasNew(bossLootBoxes > bossLastViewed)

    def __onSyncCompleted(self, *_):
        self.__updateViewModel()

    @server_settings.serverSettingsChangeListener(Configs.LOOTBOX_CONFIG.value)
    def __onServerSettingChanged(self, _):
        self.__updateViewModel()

    def __onWidgetClick(self):
        self.__boxesCtrl.updateLastViewedCount()
        with self.viewModel.transaction() as model:
            model.setHunterHasNew(False)
            model.setBossHasNew(False)
        parent = self.getParentWindow()
        showEventStorageWindow(parent)

    def __onEscKeyDown(self):
        self.onEscKeyDown()
