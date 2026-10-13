# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/battle/capture_indicators_ctrl.py
from __future__ import absolute_import
from helpers.events_handler import EventsHandler
from typing import TYPE_CHECKING
from fort_rush.gui.impl.gen.view_models.views.battle.views.fort_rush_hud_base_capture_indicator_model import FortRushHudBaseCaptureIndicatorModel, FortRushBaseCaptureState
from fort_rush.gui.impl.gen.view_models.views.battle.views.fort_rush_hud_base_marker_model import FortRushHudBaseMarkerModel
from fort_rush.gui.shared.events import CapturePointEvent
from fort_rush.gui.shared.team_utils import getTeamValue
from fort_rush_common.component_helpers import getInvaderComponent
from fort_rush_common.fort_rush_constants import CaptureStates
from gui.battle_control import avatar_getter
from gui.shared import EVENT_BUS_SCOPE, EventPriority
if TYPE_CHECKING:
    from frameworks.wulf import Array, Map
INVALID_CAPTURE_POINT_UID = -1
CAPTURE_STATE_TO_ENUM = {CaptureStates.NEUTRAL: FortRushBaseCaptureState.IDLE,
 CaptureStates.CAPTURED: FortRushBaseCaptureState.IDLE,
 CaptureStates.CAPTURING: FortRushBaseCaptureState.CAPTURING,
 CaptureStates.DECREASING: FortRushBaseCaptureState.DECAPPING,
 CaptureStates.CONTESTED: FortRushBaseCaptureState.CONTESTED}

class CaptureIndicatorsCtrl(EventsHandler):

    def __init__(self, hudRef):
        super(CaptureIndicatorsCtrl, self).__init__()
        self.__hudRef = hudRef

    def init(self):
        self._subscribe()

    def dispose(self):
        self.__hudRef = None
        self._unsubscribe()
        return

    def _getListeners(self):
        listeners = [(CapturePointEvent.CAPTURABLE_POINT_UPDATE,
          self._updateCapturePointModel,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH), (CapturePointEvent.INIT_CAPTURABLE_POINT,
          self._initCapturablePointMarker,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH)]
        return listeners

    @property
    def _capturablePointsByUid(self):
        return self.__hudRef.viewModel.getCaptureIndicatorsByUid()

    @property
    def _capturePointsMarkerArray(self):
        return self.__hudRef.viewModel.getCapturePointsMarker()

    def _createCapturablePointModel(self, uid, capturablePointName):
        model = FortRushHudBaseCaptureIndicatorModel()
        model.setUid(uid)
        model.setLabel(capturablePointName)
        self._capturablePointsByUid[uid] = model
        return model

    def _createCapturablePointMarkerModel(self, data):
        model = FortRushHudBaseMarkerModel()
        model.setLabel(data.capturablePointName)
        model.setUid(data.uid)
        with self._capturePointsMarkerArray.transaction() as tx:
            tx.addViewModel(model)
        return model

    def _getCapturablePointModel(self, uid, capturablePointName):
        indicators = self._capturablePointsByUid
        return indicators[uid] if uid in indicators else self._createCapturablePointModel(uid, capturablePointName)

    def _getCapturablePointMarkerModel(self, data):
        for model in self._capturePointsMarkerArray:
            if model.getLabel() == data.capturablePointName:
                return model

        return self._createCapturablePointMarkerModel(data)

    def _updateCapturePointModel(self, event):
        with self.__hudRef.viewModel.transaction():
            model = self._getCapturablePointModel(event.uid, event.capturablePointName)
            model.setOwnerTeam(getTeamValue(event.ownersTeam))
            model.setCapturingTeam(getTeamValue(event.invadersTeam))
            model.setState(CAPTURE_STATE_TO_ENUM[event.state])
            model.setCaptureProgress(event.captureProgressPercent)
        self._updateProgressBar(event.state)

    def _initCapturablePointMarker(self, event):
        with self.__hudRef.viewModel.transaction():
            model = self._getCapturablePointMarkerModel(event)
            self.__hudRef.markersCtrl.remove(model.proxy)
            self.__hudRef.markersCtrl.add(model.proxy, event.transform)

    def _findUidByLabel(self, capturablePointName):
        for uid, model in self._capturablePointsByUid.items():
            if model.getLabel() == capturablePointName:
                return uid

        return INVALID_CAPTURE_POINT_UID

    def _updateProgressBar(self, incomingState):
        playerVehicle = avatar_getter.getPlayerVehicle()
        if playerVehicle is None:
            self.__hudRef.viewModel.setCapturingPointUid(INVALID_CAPTURE_POINT_UID)
            return
        else:
            invasionComponent = getInvaderComponent(playerVehicle)
            if invasionComponent is None:
                self.__hudRef.viewModel.setCapturingPointUid(INVALID_CAPTURE_POINT_UID)
                return
            uid = self._findUidByLabel(invasionComponent.capturablePointName)
            if uid == INVALID_CAPTURE_POINT_UID:
                self.__hudRef.viewModel.setCapturingPointUid(INVALID_CAPTURE_POINT_UID)
                return
            if incomingState == CaptureStates.NEUTRAL:
                self.__hudRef.viewModel.setCapturingPointUid(INVALID_CAPTURE_POINT_UID)
                return
            self.__hudRef.viewModel.setCapturingPointUid(uid)
            return
