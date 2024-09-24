# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mapbox/mapbox_entry_point_view.py
import logging
from constants import Configs
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mapbox.mapbox_entry_point_view_model import MapboxEntryPointViewModel, State
from gui.impl.gen.view_models.views.lobby.common.tooltips.simple_icon_tooltip_model import HeaderType
from gui.impl.lobby.common.tooltips.simple_icon_tooltip_view import SimpleIconTooltipView
from gui.impl.pub import ViewImpl
from gui.periodic_battles.models import PeriodType
from gui.shared.utils.graphics import isRendererPipelineDeferred
from helpers import dependency, time_utils, server_settings
from skeletons.gui.game_control import IMapboxController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)
_STATE_MAPPING = {State.BEFORE: {PeriodType.BEFORE_SEASON, PeriodType.BEFORE_CYCLE, PeriodType.BETWEEN_SEASONS},
 State.ACTIVE: {PeriodType.AVAILABLE},
 State.NOTPRIMETIME: {PeriodType.NOT_AVAILABLE, PeriodType.STANDALONE_NOT_AVAILABLE, PeriodType.ALL_NOT_AVAILABLE},
 State.AFTER: {PeriodType.AFTER_CYCLE,
               PeriodType.AFTER_SEASON,
               PeriodType.NOT_AVAILABLE_END,
               PeriodType.ALL_NOT_AVAILABLE_END,
               PeriodType.STANDALONE_NOT_AVAILABLE_END}}

@dependency.replace_none_kwargs(mapboxCtrl=IMapboxController)
def isMapboxEntryPointAvailable(mapboxCtrl=None):
    return mapboxCtrl.isEnabled() and not mapboxCtrl.isFrozen() and (mapboxCtrl.getCurrentSeason() is not None or mapboxCtrl.getNextSeason() is not None)


class MapBoxEntryPointView(ViewImpl):
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(layoutID=R.views.lobby.mapbox.MapBoxEntryPointView(), flags=flags, model=MapboxEntryPointViewModel())
        super(MapBoxEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MapBoxEntryPointView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return SimpleIconTooltipView(event.getArgument('header', ''), event.getArgument('body', ''), event.getArgument('icon', ''), event.getArgument('headerType', HeaderType.NORMAL)) if contentID == R.views.lobby.common.tooltips.SimpleIconTooltip() else super(MapBoxEntryPointView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.viewModel.onActionClick, self.__onClick), (self.__mapboxCtrl.onPrimeTimeStatusUpdated, self.__onPrimeTimeUpdated), (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged))

    def _onLoading(self, *args, **kwargs):
        super(MapBoxEntryPointView, self)._onLoading(*args, **kwargs)
        self.__invalidate()

    def __onClick(self):
        periodInfo = self.__mapboxCtrl.getPeriodInfo(time_utils.getCurrentTimestamp())
        state = self.__getEntryPointState(periodInfo)
        if state == State.BEFORE:
            self.__mapboxCtrl.showMapboxInfoPage()
        else:
            self.__mapboxCtrl.selectMapboxBattle()

    @server_settings.serverSettingsChangeListener(Configs.MAPBOX_CONFIG.value)
    def __onServerSettingsChanged(self, _):
        self.__invalidate()

    def __onPrimeTimeUpdated(self, _):
        self.__invalidate()

    def __invalidate(self):
        if not isMapboxEntryPointAvailable():
            self.destroy()
            return
        now = time_utils.getCurrentTimestamp()
        periodInfo = self.__mapboxCtrl.getPeriodInfo(now)
        state = self.__getEntryPointState(periodInfo)
        startTime = endTime = leftTime = -1
        if state == State.ACTIVE:
            endTime = periodInfo.cycleBorderRight.timestamp
            leftTime = time_utils.getTimeDeltaFromNowInLocal(endTime)
        elif state == State.BEFORE:
            startTime = periodInfo.cycleBorderRight.timestamp
            nextSeason = self.__mapboxCtrl.getNextSeason(now)
            cycle = nextSeason.getNextByTimeCycle(now)
            endTime = cycle.endDate
            leftTime = time_utils.getTimeDeltaFromNowInLocal(startTime)
        elif state == State.NOTPRIMETIME:
            leftTime = self.__mapboxCtrl.getLeftTimeToPrimeTimesEnd(now)
        with self.viewModel.transaction() as model:
            model.setState(state)
            model.setStartTime(startTime)
            model.setEndTime(endTime)
            model.setLeftTime(leftTime)
            model.setPerformanceAlertEnabled(not isRendererPipelineDeferred())

    @staticmethod
    def __getEntryPointState(periodInfo):
        periodType = periodInfo.periodType
        for bannerState, periodTypes in _STATE_MAPPING.items():
            if periodType in periodTypes:
                return bannerState

        return State.UNDEFINED
