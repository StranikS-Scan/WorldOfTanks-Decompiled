# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_performance_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.game_control.event_battles_controller import WtPerfProblems
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_entry_point_model import WtEventEntryPointModel
from gui.impl.pub import ViewImpl
from helpers import dependency, server_settings
from skeletons.gui.game_control import IEventBattlesController
from constants import Configs
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class WtEventPerformanceTooltipView(ViewImpl):
    __slots__ = ()
    __eventController = dependency.descriptor(IEventBattlesController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.wt_event.tooltips.WtEventPerformanceTooltipView())
        settings.model = WtEventEntryPointModel()
        super(WtEventPerformanceTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventPerformanceTooltipView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def _getEvents(self):
        return ((self.__eventController.onUpdated, self.__onUpdated), (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged), (self.__itemsCache.onSyncCompleted, self.__onCacheResync))

    def __onUpdated(self, *_):
        self.__updateViewModel()

    def __updateViewModel(self):
        performanceRisk = self.__eventController.analyzeClientSystem()
        with self.viewModel.transaction() as tx:
            tx.setPerformanceRisk(WtPerfProblems.getPerformanceRiskMap(performanceRisk))

    @server_settings.serverSettingsChangeListener(Configs.EVENT_BATTLES_CONFIG.value)
    def __onServerSettingsChanged(self, _):
        self.__updateViewModel()

    def __onCacheResync(self, _, __):
        self.__updateViewModel()
