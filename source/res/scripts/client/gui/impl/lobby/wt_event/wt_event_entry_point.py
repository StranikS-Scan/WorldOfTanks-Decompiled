# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_entry_point.py
from constants import Configs
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_entry_point_model import WtEventEntryPointModel
from gui.impl.lobby.wt_event.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.utils.scheduled_notifications import Notifiable
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from helpers import dependency, server_settings
from skeletons.gui.game_control import IGameEventController, ILootBoxesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(eventController=IGameEventController)
def isWTEventEntryPointAvailable(eventController=None):
    return eventController.isEnabled()


class WTEventEntryPoint(ViewImpl, Notifiable):
    __boxesCtrl = dependency.descriptor(ILootBoxesController)
    __eventController = dependency.descriptor(IGameEventController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.wt_event.WTEventEntryPoint())
        settings.flags = flags
        settings.model = WtEventEntryPointModel()
        super(WTEventEntryPoint, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.wt_event.tooltips.WtEventLootBoxTooltipView():
            lootBoxType = event.getArgument('type')
            return WtEventLootBoxTooltipView(isHunterLootBox=lootBoxType == 'hunter')
        return super(WTEventEntryPoint, self).createToolTipContent(event, contentID)

    def _finalize(self):
        self.__removeListeners()
        super(WTEventEntryPoint, self)._finalize()

    @property
    def viewModel(self):
        return super(WTEventEntryPoint, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WTEventEntryPoint, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__updateViewModel()

    def __addListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__itemsCache.onSyncCompleted += self.__onCacheResync
        self.viewModel.onClick += self.__onClick
        self.__eventController.onUpdated += self.__onUpdated
        self.__eventController.onPrimeTimeStatusUpdated += self.__onUpdated
        self.__eventController.onGameEventTick += self.__onUpdated

    def __removeListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__itemsCache.onSyncCompleted -= self.__onCacheResync
        self.viewModel.onClick -= self.__onClick
        self.__eventController.onUpdated -= self.__onUpdated
        self.__eventController.onPrimeTimeStatusUpdated -= self.__onUpdated
        self.__eventController.onGameEventTick -= self.__onUpdated

    @server_settings.serverSettingsChangeListener(Configs.EVENT_BATTLES_CONFIG.value)
    def __onServerSettingsChanged(self, _):
        self.__updateViewModel()

    def __onCacheResync(self, _, __):
        self.__updateViewModel()

    def __onClick(self):
        self.__eventController.doSelectEventPrb()
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.EVENT)

    def __onUpdated(self, *_):
        self.__updateViewModel()

    def __updateViewModel(self):
        if self.__eventController.isEnabled():
            hunterLootBoxes = self.__boxesCtrl.getLootBoxesCountByType(EventLootBoxes.WT_HUNTER)
            bossLootBoxes = self.__boxesCtrl.getLootBoxesCountByType(EventLootBoxes.WT_BOSS)
            with self.viewModel.transaction() as model:
                model.setHunterLootBoxesCount(hunterLootBoxes)
                model.setBossLootBoxesCount(bossLootBoxes)
            with self.viewModel.transaction() as tx:
                tx.setState(self.__getState())
                if self.__eventController.isModeActive():
                    tx.setEndDate(self.__eventController.getEventEndTimestamp() or -1)
        else:
            self.destroy()

    def __getState(self):
        return WtEventEntryPointModel.STATE_ACTIVE if self.__eventController.isInPrimeTime() and not self.__eventController.isFrozen() else WtEventEntryPointModel.STATE_NOBATTLE
