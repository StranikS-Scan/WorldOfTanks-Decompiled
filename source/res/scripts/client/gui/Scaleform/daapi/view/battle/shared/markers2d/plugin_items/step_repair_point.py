# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/plugin_items/step_repair_point.py
import logging
from gui.Scaleform.daapi.view.battle.shared.markers2d import plugins
from gui.battle_control.battle_constants import PROGRESS_CIRCLE_TYPE
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from helpers import time_utils
from Math import Vector4, Vector2
_logger = logging.getLogger(__name__)
_SECTOR_BASES_BOUNDS_MIN_SCALE = Vector2(1.0, 1.0)
_MEDIUM_MARKER_MIN_SCALE = 100
_EMPTY_MARKER_BOUNDS = Vector4(0.0, 0.0, 0.0, 0.0)
_EMPTY_MARKER_INNER_BOUNDS = Vector4(0.0, 0.0, 0.0, 0.0)
_MAX_CULL_DISTANCE = 1000000.0
_SMALL_MARKER_MIN_SCALE = 40
_NEAR_MARKER_CULL_DISTANCE = 300

class StepRepairPointPlugin(plugins.MarkerPlugin):
    __slots__ = ('__markers',)

    def __init__(self, parentObj):
        super(StepRepairPointPlugin, self).__init__(parentObj)
        self.__markers = {}

    def init(self):
        super(StepRepairPointPlugin, self).init()
        stepRepairPointComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.onStepRepairPointAdded += self._onStepRepairPointAdded
            stepRepairPointComponent.onStepRepairPointActiveStateChanged += self._onStepRepairPointActiveStateChanged
        else:
            _logger.error('Expected StepRepairPointComponent not present!')
        progressCtrl = self.sessionProvider.dynamic.progressTimer
        if progressCtrl is not None:
            progressCtrl.onTimerUpdated += self._onTimerUpdated
            progressCtrl.onCircleStatusChanged += self._onCircleStatusChanged
            progressCtrl.onVehicleEntered += self._onVehicleEntered
            progressCtrl.onVehicleLeft += self._onVehicleLeft
        return

    def fini(self):
        stepRepairPointComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.onStepRepairPointAdded -= self._onStepRepairPointAdded
            stepRepairPointComponent.onStepRepairPointActiveStateChanged -= self._onStepRepairPointActiveStateChanged
        ctrl = self.sessionProvider.dynamic.progressTimer
        if ctrl is not None:
            ctrl.onTimerUpdated -= self._onTimerUpdated
            ctrl.onCircleStatusChanged -= self._onCircleStatusChanged
            ctrl.onVehicleEntered -= self._onVehicleEntered
            ctrl.onVehicleLeft -= self._onVehicleLeft
        super(StepRepairPointPlugin, self).fini()
        return

    def start(self):
        super(StepRepairPointPlugin, self).start()
        progressCtrl = self.sessionProvider.dynamic.progressTimer
        stepRepairPointComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            repairPts = stepRepairPointComponent.stepRepairPoints
            for pt in repairPts:
                self._onStepRepairPointAdded(pt)
                inCircle, state = progressCtrl.getPlayerCircleState(PROGRESS_CIRCLE_TYPE.SECTOR_BASE_CIRCLE, pt.id)
                if inCircle:
                    self._onVehicleEntered(PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE, pt.id, state)

        else:
            _logger.error('Expected StepRepairPointComponent not present!')
        return

    def stop(self):
        for markerID in self.__markers.values():
            self._destroyMarker(markerID)

        self.__markers.clear()
        super(StepRepairPointPlugin, self).stop()

    def _onStepRepairPointAdded(self, stepRepairPoint):
        handle = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.STEP_REPAIR_MARKER_TYPE, stepRepairPoint.position + settings.MARKER_POSITION_ADJUSTMENT)
        if handle is None:
            return
        else:
            self._setMarkerActive(handle, stepRepairPoint.isActiveForPlayerTeam())
            self._setMarkerRenderInfo(handle, _SMALL_MARKER_MIN_SCALE, _EMPTY_MARKER_BOUNDS, _EMPTY_MARKER_INNER_BOUNDS, _NEAR_MARKER_CULL_DISTANCE, _SECTOR_BASES_BOUNDS_MIN_SCALE)
            self.__markers[stepRepairPoint.id] = handle
            return

    def _onVehicleEntered(self, type_, idx, state):
        if type_ != PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        else:
            handle = self.__markers[idx]
            if handle is not None:
                self._invokeMarker(handle, 'notifyVehicleInCircle', True)
                self._parentObj.invokeMarker(handle, 'setState', [state])
            return

    def _onVehicleLeft(self, type_, idx):
        if type_ != PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        else:
            handle = self.__markers[idx]
            if handle is not None:
                self._invokeMarker(handle, 'notifyVehicleInCircle', False)
            return

    def _onTimerUpdated(self, type_, pointId, timeLeft):
        if type_ is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        handle = self.__markers[pointId]
        self._parentObj.invokeMarker(handle, 'setCooldown', [time_utils.getTimeLeftFormat(timeLeft)])

    def _onCircleStatusChanged(self, type_, pointId, state):
        if type_ is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        handle = self.__markers[pointId]
        self._parentObj.invokeMarker(handle, 'setState', [state])

    def _onStepRepairPointActiveStateChanged(self, pointId, isActive):
        handle = self.__markers[pointId]
        if handle is not None:
            self._setMarkerActive(handle, isActive)
        return
