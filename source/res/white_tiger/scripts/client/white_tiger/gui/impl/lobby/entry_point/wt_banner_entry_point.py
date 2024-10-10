# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/entry_point/wt_banner_entry_point.py
from frameworks.wulf import ViewFlags, ViewSettings
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.entry_point_model import EntryPointModel, State
from white_tiger.gui.impl.lobby.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from white_tiger.gui.impl.lobby.tooltips.wt_event_battles_end_tooltip_view import WtEventBattlesEndTooltipView
from gui.shared.utils.scheduled_notifications import Notifiable
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from helpers import dependency, server_settings
from skeletons.gui.game_control import IWhiteTigerController, ILootBoxesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.wt_event.wt_event_helpers import getSecondsLeft
from gui.periodic_battles.models import PrimeTimeStatus

@dependency.replace_none_kwargs(wtController=IWhiteTigerController)
def isWTBannerEntryPointAvailable(wtController=None):
    return wtController.isEnabled()


class WTEventEntryPoint(ViewImpl, Notifiable):
    __boxesCtrl = dependency.descriptor(ILootBoxesController)
    __wtController = dependency.descriptor(IWhiteTigerController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.white_tiger.lobby.EntryPoint())
        settings.flags = flags
        settings.model = EntryPointModel()
        super(WTEventEntryPoint, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.white_tiger.lobby.tooltips.LootBoxTooltipView():
            lootBoxType = event.getArgument('type')
            return WtEventLootBoxTooltipView(isHunterLootBox=lootBoxType == 'hunter')
        return WtEventBattlesEndTooltipView() if contentID == R.views.white_tiger.lobby.tooltips.BattlesEndTooltipView() else super(WTEventEntryPoint, self).createToolTipContent(event, contentID)

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
        self.__wtController.onUpdated += self.__onUpdated
        self.__wtController.onPrimeTimeStatusUpdated += self.__onUpdated
        self.__wtController.onGameEventTick += self.__onUpdated

    def __removeListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__itemsCache.onSyncCompleted -= self.__onCacheResync
        self.viewModel.onClick -= self.__onClick
        self.__wtController.onUpdated -= self.__onUpdated
        self.__wtController.onPrimeTimeStatusUpdated -= self.__onUpdated
        self.__wtController.onGameEventTick -= self.__onUpdated

    @server_settings.serverSettingsChangeListener('white_tiger_config')
    def __onServerSettingsChanged(self, _):
        self.__updateViewModel()

    def __onCacheResync(self, _, __):
        self.__updateViewModel()

    def __onClick(self):
        self.__wtController.doSelectEventPrb()
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.EVENT)

    def __onUpdated(self, *_):
        self.__updateViewModel()

    def __updateViewModel(self):
        if self.__wtController.isEnabled():
            status, timeLeft, _ = self.__wtController.getPrimeTimeStatus()
            secondsLeft = getSecondsLeft()
            if status == PrimeTimeStatus.NOT_AVAILABLE:
                secondsLeft = timeLeft
            with self.viewModel.transaction() as tx:
                tx.setHunterLootBoxesCount(self.__boxesCtrl.getLootBoxesCountByTypeForUI(WhiteTigerLootBoxes.WT_HUNTER))
                tx.setBossLootBoxesCount(self.__boxesCtrl.getLootBoxesCountByTypeForUI(WhiteTigerLootBoxes.WT_BOSS))
                tx.setState(self.__getState())
                tx.setTimeLeft(secondsLeft)
        else:
            self.destroy()

    def __getState(self):
        if self.__wtController.isInPrimeTime() and not self.__wtController.isFrozen():
            return State.ACTIVE
        return State.BATTLES_END if self.__wtController.isBattlesEnd() else State.LOCKED
