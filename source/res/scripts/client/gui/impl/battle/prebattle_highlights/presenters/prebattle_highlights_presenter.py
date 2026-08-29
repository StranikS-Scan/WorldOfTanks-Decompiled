# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/prebattle_highlights/presenters/prebattle_highlights_presenter.py
from __future__ import absolute_import
import logging
import weakref
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.battle.prebattle_highlights.presenters.statistics_sub_presenter import StatisticsSubPresenter
from gui.impl.battle.prebattle_highlights.presenters.vehicle_markers_sub_presenter import VehicleMarkersSubPresenter
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class PrebattleHighlightsPresenter(SubModelPresenter):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, viewModel, parentView, pbhCtrl):
        super(PrebattleHighlightsPresenter, self).__init__(viewModel, parentView)
        self._subPresenters = []
        self._pbhCtrl = weakref.proxy(pbhCtrl)
        self.addSubPresenter(VehicleMarkersSubPresenter(viewModel.getMarkers(), parentView))
        self.addSubPresenter(StatisticsSubPresenter(viewModel.getPlayersStats(), parentView))

    def addSubPresenter(self, subPresenter):
        self._subPresenters.append(subPresenter)

    def packModel(self):
        model = self.getViewModel()
        vehicleCamouflageKind = self.__sessionProvider.arenaVisitor.type.getVehicleCamouflageKind()
        meetsHistoricalCompliance = self._pbhCtrl.meetsHistoricalCompliance
        model.setMapType(vehicleCamouflageKind)
        model.setCurrentState(model.PBH_INTRO)
        model.setHistoricalCompliance(meetsHistoricalCompliance)
        _logger.debug('[PBH] pack model in presenter')
        for subPresenter in self._subPresenters:
            subPresenter.packModel()

    def finalize(self):
        _logger.debug('[PBH] PrebattleHighlightsPresenter finalize')
        super(PrebattleHighlightsPresenter, self).finalize()
        self._subPresenters = []

    def _getEvents(self):
        pbhCtrlEvents = ((self._pbhCtrl.onStartPbhStage, self.__onStartPbhStage),) if self._pbhCtrl is not None else ()
        return pbhCtrlEvents

    def __onStartPbhStage(self):
        _logger.debug('[PBH] stage state')
        model = self.getViewModel()
        model.setCurrentState(model.PBH_STAGE)
