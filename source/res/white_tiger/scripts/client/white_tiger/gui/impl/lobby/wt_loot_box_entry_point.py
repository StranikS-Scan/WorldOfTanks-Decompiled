# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_loot_box_entry_point.py
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_loot_box_entry_point_model import WtLootBoxEntryPointModel
from white_tiger.gui.impl.lobby.tooltips.wt_lootboxes_tooltip_view import WtLootBoxesTooltipView
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes
from white_tiger.gui.impl.lobby.wt_event_inject_widget_view import WTEventInjectWidget
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.view.meta.WTEventBoxEntryPointWidgetMeta import WTEventBoxEntryPointWidgetMeta
from gui.shared.event_dispatcher import showEventStorageWindow
from helpers import dependency, server_settings
from skeletons.gui.game_control import ILootBoxesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class WTEventLootBoxEntrancePointWidget(WTEventBoxEntryPointWidgetMeta, WTEventInjectWidget):

    def _makeInjectView(self):
        return LootboxesEntrancePointWidget()


class LootboxesEntrancePointWidget(ViewImpl):
    __boxesCtrl = dependency.descriptor(ILootBoxesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.white_tiger.lobby.LootBoxesEntryPoint(), flags=ViewFlags.VIEW, model=WtLootBoxEntryPointModel())
        settings.args = args
        settings.kwargs = kwargs
        super(LootboxesEntrancePointWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return WtLootBoxesTooltipView() if contentID == R.views.white_tiger.lobby.tooltips.LootBoxesTooltipView() else super(LootboxesEntrancePointWidget, self).createToolTipContent(event, contentID)

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

    def __removeListeners(self):
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.viewModel.onWidgetClick -= self.__onWidgetClick

    def __updateViewModel(self):
        hunterLootBoxes = self.__boxesCtrl.getLootBoxesCountByTypeForUI(WhiteTigerLootBoxes.WT_HUNTER)
        bossLootBoxes = self.__boxesCtrl.getLootBoxesCountByTypeForUI(WhiteTigerLootBoxes.WT_BOSS)
        hunterLastViewed, bossLastViewed = self.__boxesCtrl.getLastViewedCount()
        with self.viewModel.transaction() as model:
            model.setHunterLootBoxesCount(hunterLootBoxes)
            model.setBossLootBoxesCount(bossLootBoxes)
            model.setHunterHasNew(hunterLootBoxes > hunterLastViewed)
            model.setBossHasNew(bossLootBoxes > bossLastViewed)

    def __onSyncCompleted(self, *_):
        self.__updateViewModel()

    @server_settings.serverSettingsChangeListener('lootBoxes_config')
    def __onServerSettingChanged(self, _):
        self.__updateViewModel()

    def __onWidgetClick(self):
        self.__boxesCtrl.updateLastViewedCount()
        with self.viewModel.transaction() as model:
            model.setHunterHasNew(False)
            model.setBossHasNew(False)
        parent = self.getParentWindow()
        showEventStorageWindow(parent)
