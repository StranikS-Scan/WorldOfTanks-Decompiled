# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/cgf/capture_point.py
from __future__ import absolute_import
import logging
from functools import partial
from helpers.CallbackDelayer import CallbackDelayer
import CGF
import DebugDrawer
import Math
from CapturePointComponent import CapturePointComponent, CapturePointMarkerAnchor
from GenericComponents import Sequence
from cgf_modules.variable_components import VariableStorageComponent
from constants import IS_CLIENT
from fort_rush.gui.shared.events import CapturePointEvent
from fort_rush.helpers.utils import getCurrentTeam
from fort_rush_common.fort_rush_constants import CAPTURE_POINT_NO_TEAM
from fort_rush_common.fort_rush_constants import CaptureStates
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
if IS_CLIENT:
    from fort_rush.gui.impl.battle.capture_indicators_ctrl import INVALID_CAPTURE_POINT_UID
else:
    INVALID_CAPTURE_POINT_UID = -1
_logger = logging.getLogger(__name__)
MARKER_ANCHOR_GIZMO_COLOUR = 13385641
MARKER_ANCHOR_GIZMO_SCALE = Math.Vector3(1, 1, 1)
COMPATIBLE_VFX_STATES = (CaptureStates.NEUTRAL, CaptureStates.CAPTURED, CaptureStates.CONTESTED)

class ZoneVFXStates(object):
    DEFAULT = 1
    NEUTRAL = 2
    ALLY_CAPTURED = 3
    ENEMY_CAPTURED = 4
    ALLY_CONTESTED = 5
    ENEMY_CONTESTED = 6
    CONTESTED_TO_ALLY = 7
    CONTESTED_TO_ENEMY = 8


class CapturePointSystem(CGF.System):
    Activated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(CapturePointComponent), CGF.Ro(CGF.TransformComponent))
    Removed = CGF.RemoveReaction(CGF.GameObject, CGF.ReactRw(CapturePointComponent), CGF.Ro(CGF.TransformComponent))
    VariableStorageAccess = CGF.AccessReaction(CGF.Rw(VariableStorageComponent))
    SequenceAccess = CGF.AccessReaction(CGF.Rw(Sequence))
    MarkerAnchorAccess = CGF.AccessReaction(CGF.Ro(CapturePointMarkerAnchor), CGF.Ro(CGF.TransformComponent))
    Reactions = CGF.Reactions(Removed, Activated, VariableStorageAccess, SequenceAccess, MarkerAnchorAccess)

    def __init__(self):
        super(CapturePointSystem, self).__init__()
        self._delayer = CallbackDelayer()

    def onMappingUnloaded(self):
        self._delayer.destroy()

    def update(self):
        for _go, capturePointComponent, _transform in self.reaction(self.Removed):
            capturePointComponent.onCaptureStateChanged -= self.updateSequence

        for go, capturePointComponent, transform in self.reaction(self.Activated):
            self.onActivate(go, capturePointComponent, transform)

    def onActivate(self, go, capturePointComponent, transform):
        _logger.debug('[FORT_RUSH] CapturePointManager.onCapturePointAdded: %s', capturePointComponent.capturablePointName)
        capturePointComponent.onCaptureStateChanged += self.updateSequence
        self._dispatchInitEvent(go, capturePointComponent, transform)
        capturePointComponent.sendEventImmediately()

    def _dispatchInitEvent(self, go, capturePointComponent, transform):
        uid = go.id
        if uid == INVALID_CAPTURE_POINT_UID:
            _logger.warning('[FORT_RUSH] CapturePointEvent.INIT_CAPTURABLE_POINT dispatched with invalid UID for capturablePointName=%s', capturePointComponent.capturablePointName)
            return
        markerTransform = self._findMarkerAnchorTransform(go) or transform
        newMatrix = Math.Matrix(markerTransform.worldTransform)
        g_eventBus.handleEvent(CapturePointEvent(eventType=CapturePointEvent.INIT_CAPTURABLE_POINT, capturablePointName=capturePointComponent.capturablePointName, transform=newMatrix, uid=uid), EVENT_BUS_SCOPE.BATTLE)

    def _findMarkerAnchorTransform(self, go):
        anchorAccess = self.reaction(self.MarkerAnchorAccess)
        for _anchor, anchorTransform in CGF.findInHierarchyWithReaction(go, anchorAccess, False):
            return anchorTransform

        return None

    def updateSequence(self, go, point, prevState):
        _logger.debug('[FORT_RUSH] CapturePointManager.updateSequence')
        captureState = point.state
        if captureState not in COMPATIBLE_VFX_STATES:
            return
        else:
            sequenceAccess = self.reaction(self.SequenceAccess)
            sequenceComponent = None
            for component in CGF.findInHierarchyWithReaction(go, sequenceAccess):
                sequenceComponent = component
                break

            if not sequenceComponent:
                _logger.warning('[FORT_RUSH][CAPTURE_POINT_SYSTEM] updateSequence - Capture point %s has missing sequence component', point.capturablePointName)
                return
            layerIndex = self._evaluateSequenceLayer(point, prevState)
            if sequenceComponent.activeLayerIdx == layerIndex:
                return
            sequenceComponent.stop()
            self._delayer.delayCallback(0.01, partial(self._switchLayer, go, layerIndex))
            return

    def _evaluateSequenceLayer(self, point, prevState):
        if point.state == CaptureStates.CAPTURED:
            playerTeam = getCurrentTeam()
            if playerTeam == point.capturablePointOwnerTeam:
                if prevState != CaptureStates.CONTESTED:
                    return ZoneVFXStates.ALLY_CAPTURED
                return ZoneVFXStates.CONTESTED_TO_ALLY
            if prevState != CaptureStates.CONTESTED:
                return ZoneVFXStates.ENEMY_CAPTURED
            return ZoneVFXStates.CONTESTED_TO_ENEMY
        if point.state == CaptureStates.CONTESTED:
            playerTeam = getCurrentTeam()
            if point.capturablePointOwnerTeam != CAPTURE_POINT_NO_TEAM:
                if playerTeam == point.capturablePointOwnerTeam:
                    return ZoneVFXStates.ALLY_CONTESTED
                return ZoneVFXStates.ENEMY_CONTESTED
        return ZoneVFXStates.NEUTRAL

    def _switchLayer(self, go, layerIndex):
        variableStorageAccess = self.reaction(self.VariableStorageAccess)
        variableStorage = variableStorageAccess.find(go)
        if not variableStorage:
            return
        variableStorage.modify(go, 'captureZone/state', layerIndex)


class CapturePointMarkerAnchorGizmoSystem(CGF.System):
    MarkerAnchorsReaction = CGF.IterateReaction(CGF.ActiveOnly, CGF.Ro(CapturePointMarkerAnchor), CGF.Ro(CGF.TransformComponent))
    Reactions = CGF.Reactions(MarkerAnchorsReaction)

    def update(self):
        for _anchor, transform in self.reaction(self.MarkerAnchorsReaction):
            DebugDrawer.DebugDrawer().sphere().wireframe(False).colour(MARKER_ANCHOR_GIZMO_COLOUR).position(transform.worldPosition).scale(MARKER_ANCHOR_GIZMO_SCALE)
