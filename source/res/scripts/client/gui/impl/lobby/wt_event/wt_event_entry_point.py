# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_entry_point.py
from constants import Configs
from frameworks.wulf import ViewFlags, ViewSettings
from gui.game_control.event_battles_controller import WtPerfProblems
from gui.impl.lobby.wt_event.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_event_performance_tooltip_view import WtEventPerformanceTooltipView
from gui.impl.lobby.wt_event.wt_event_constants import WtState
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_entry_point_model import WtEventEntryPointModel, State
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_model import PortalType
from gui.periodic_battles.models import PeriodType
from gui.shared.event_dispatcher import showEventPortalWindow
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.utils.scheduled_notifications import Notifiable
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES, PREBATTLE_ACTION_NAME
from helpers import dependency, server_settings
from skeletons.gui.game_control import IEventBattlesController, IWTLootBoxesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_ENTRY_POINT_STATE_MAP = {WtState.BEFORE_SEASON: State.BEFORE,
 WtState.AFTER_SEASON: State.AFTER,
 WtState.NOT_AVAILABLE: State.NOTPRIMETIME,
 WtState.AVAILABLE: State.ACTIVE}

@dependency.replace_none_kwargs(eventController=IEventBattlesController)
def isWTEventEntryPointAvailable(eventController=None):
    return eventController.isEnabled()


class WTEventEntryPoint(ViewImpl, Notifiable):
    __boxesCtrl = dependency.descriptor(IWTLootBoxesController)
    __eventController = dependency.descriptor(IEventBattlesController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.wt_event.WTEventEntryPoint())
        settings.flags = flags
        settings.model = WtEventEntryPointModel()
        self.__isSingle = True
        super(WTEventEntryPoint, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.wt_event.tooltips.WtEventPerformanceTooltipView():
            return WtEventPerformanceTooltipView()
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

    def setIsSingle(self, value):
        self.__isSingle = value
        self.__updateViewModel()

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
        if self.__getState() is State.AFTER:
            showEventPortalWindow(portalType=PortalType.BOSS)
        else:
            self.__eventController.doSelectEventPrb()
            selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.EVENT)

    def __onUpdated(self, *_):
        self.__updateViewModel()

    def __updateViewModel(self):
        if self.__eventController.isEnabled():
            performanceRisk = self.__eventController.analyzeClientSystem()
            periodInfo = self.__eventController.getPeriodInfo()
            state = self.__getState()
            with self.viewModel.transaction() as tx:
                tx.setHunterLootBoxesCount(self.__boxesCtrl.getLootBoxesCountByTypeForUI(EventLootBoxes.WT_HUNTER))
                tx.setBossLootBoxesCount(self.__boxesCtrl.getLootBoxesCountByTypeForUI(EventLootBoxes.WT_BOSS))
                tx.setState(state)
                tx.setEndTime(self.__getEndDate())
                tx.setIsSingle(self.__isSingle)
                tx.setPerformanceRisk(WtPerfProblems.getPerformanceRiskMap(performanceRisk))
                tx.setIsNew(not selectorUtils.isKnownBattleType(PREBATTLE_ACTION_NAME.EVENT_BATTLE))
                if state in (State.BEFORE, State.ACTIVE):
                    tx.setLeftTime(periodInfo.cycleBorderRight.delta(periodInfo.now))
                elif state == State.NOTPRIMETIME:
                    tx.setLeftTime(periodInfo.primeDelta)
                tx.setStartTime(self.__getStartDate())
        else:
            self.destroy()

    def __getState(self):
        periodInfo = self.__eventController.getPeriodInfo()
        state = State.NOTPRIMETIME
        if periodInfo.periodType in (PeriodType.BEFORE_SEASON, PeriodType.BEFORE_CYCLE, PeriodType.BETWEEN_SEASONS):
            state = State.BEFORE
        elif periodInfo.periodType in (PeriodType.AFTER_SEASON,
         PeriodType.AFTER_CYCLE,
         PeriodType.ALL_NOT_AVAILABLE_END,
         PeriodType.NOT_AVAILABLE_END,
         PeriodType.STANDALONE_NOT_AVAILABLE_END):
            state = State.AFTER
        elif self.__eventController.isInPrimeTime() and not self.__eventController.isFrozen():
            state = State.ACTIVE
        return state

    def __getEndDate(self):
        return self.__eventController.getEndTime()

    def __getStartDate(self):
        return self.__eventController.getStartTime()
