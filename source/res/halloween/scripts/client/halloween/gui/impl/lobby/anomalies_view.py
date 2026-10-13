# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/anomalies_view.py
from __future__ import absolute_import
from frameworks.wulf import WindowFlags
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen import R
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from halloween.gui.impl.common.anomalies_view_mixin import AnomaliesViewMixin
from halloween.gui.impl.gen.view_models.views.common.anomaly_model import AnomalyState as AState
from halloween.gui.impl.gen.view_models.views.lobby.anomalies_view_model import AnomaliesViewModel
from halloween.gui.impl.lobby.hw_helpers.anomalies_helpers import getKnownAnomaliesIDs, setAnomalyAsShowed, getShowedAnomaliesIDs
from halloween.gui.impl.lobby.tooltips.anomaly_tooltip import AnomalyTooltipView
from halloween.gui.sounds import playSound
from halloween.gui.sounds.sound_constants import AnomaliesSounds
from halloween.skeletons.halloween_anomalies_controller import IHalloweenAnomaliesController
from halloween.uilogging.loggers import HWMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys, HWLogActions
from helpers import dependency

class AnomaliesView(AnomaliesViewMixin, ViewComponent):
    _MAX_SKIN_ID = R.images.halloween.gui.maps.icons.anomalies_view.bg.length()
    _hwAnomaliesCtrl = dependency.descriptor(IHalloweenAnomaliesController)

    def __init__(self):
        super(AnomaliesView, self).__init__(R.views.halloween.mono.lobby.anomalies(), AnomaliesViewModel)
        self.__uiLogger = HWMetricsLogger(HWLogKeys.ANOMALIES_VIEW)

    def getAnomalyState(self, anomalyData):
        if self.isAnomalyKnown(anomalyData):
            if anomalyData.id in getShowedAnomaliesIDs():
                return AState.ACQUIRED
            return AState.NEW
        return AState.UNKNOWN

    @property
    def knownAnomaliesIDs(self):
        return getKnownAnomaliesIDs()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.halloween.mono.lobby.tooltips.anomaly_tooltip():
            anomaly = self._hwAnomaliesCtrl.getAnomalyByID(event.getArgument('id'))
            state = self.getAnomalyState(anomaly)
            return AnomalyTooltipView(anomaly, state)
        return super(AnomaliesView, self).createToolTipContent(event, contentID)

    @property
    def viewModel(self):
        return super(AnomaliesView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.matrix.onAnomalyAcknowledged, self.__onAnomalyAcknowledged), (self._hwAnomaliesCtrl.onRefreshData, self.__onRefreshData))

    def _onLoading(self, *args, **kwargs):
        skinId = self._hwAnomaliesCtrl.getNextSkinId(self._MAX_SKIN_ID)
        self.viewModel.setSkinId(skinId)
        super(AnomaliesView, self)._onLoading()
        self.__uiLogger.onStartView(HWLogActions.LIFETIME)

    def _initialize(self, *args, **kwargs):
        super(AnomaliesView, self)._initialize(*args, **kwargs)
        playSound(AnomaliesSounds.Hangar.ENTER)

    def _finalize(self):
        playSound(AnomaliesSounds.Hangar.LEAVE)
        self.__uiLogger.onStopView(HWLogActions.LIFETIME)
        super(AnomaliesView, self)._finalize()

    def __onClose(self):
        state = getLobbyStateMachine().getStateFromView(self)
        if state:
            state.goBack()

    def __onAnomalyAcknowledged(self, args):
        setAnomalyAsShowed(args.get('id'))
        self.refreshMatrix()

    def __onRefreshData(self):
        self.refreshMatrix()


class AnomaliesWindow(WindowImpl):

    def __init__(self, layer, **_):
        super(AnomaliesWindow, self).__init__(content=AnomaliesView(), wndFlags=WindowFlags.WINDOW, layer=layer)
