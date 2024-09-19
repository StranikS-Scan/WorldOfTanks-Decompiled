# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_loot_box_entry_point.py
from constants import Configs, QUEUE_TYPE, PREBATTLE_TYPE
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_loot_box_entry_point_model import WtEventLootBoxEntryPointModel
from gui.impl.lobby.wt_event.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from gui.impl.lobby.wt_event.wt_event_popover import WTEventLootBoxesPopover
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.loot_box import EventLootBoxes
from helpers import dependency, server_settings
from skeletons.gui.game_control import IWTLootBoxesController, IEventBattlesController
from skeletons.gui.hangar import ICarouselEventEntry
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_ENABLED_PRE_QUEUES = (QUEUE_TYPE.RANDOMS, QUEUE_TYPE.EVENT_BATTLES)
_ENABLED_PRE_BATTLES = (PREBATTLE_TYPE.SQUAD, PREBATTLE_TYPE.TRAINING, PREBATTLE_TYPE.EVENT)

class WTEventLootBoxEntrancePointWidget(ViewImpl, ICarouselEventEntry):
    __boxesCtrl = dependency.descriptor(IWTLootBoxesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameEventController = dependency.descriptor(IEventBattlesController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wt_event.WTEventBoxEntryPoint(), flags=ViewFlags.VIEW, model=WtEventLootBoxEntryPointModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WTEventLootBoxEntrancePointWidget, self).__init__(settings)

    @staticmethod
    def getIsActive(state):
        return WTEventLootBoxEntrancePointWidget.__gameEventController.isEnabled() and (any((state.isInPreQueue(preQueue) for preQueue in _ENABLED_PRE_QUEUES)) or any((state.isInUnit(preBattle) for preBattle in _ENABLED_PRE_BATTLES)))

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return WtEventLootBoxTooltipView(isHunterLootBox=event.getArgument('isHunterLootBox')) if contentID == R.views.lobby.wt_event.tooltips.WtEventLootBoxTooltipView() else super(WTEventLootBoxEntrancePointWidget, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        return WTEventLootBoxesPopover(isHunterLootBox=event.getArgument('isHunterLootBox'))

    def _onLoading(self, *args, **kwargs):
        super(WTEventLootBoxEntrancePointWidget, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__updateViewModel()

    def _finalize(self):
        self.__removeListeners()
        super(WTEventLootBoxEntrancePointWidget, self)._finalize()

    def __addListeners(self):
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def __removeListeners(self):
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged

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
