# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/area_marker_ctrl.py
import logging
import BigWorld
from helpers import dependency
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_controller import BaseMarkerController
_logger = logging.getLogger(__name__)

class AreaMarkersController(BaseMarkerController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(AreaMarkersController, self).__init__()
        self._battleCtx = None
        self._arenaVisitor = None
        self._prevGlobalVisibility = None
        return

    def startControl(self, battleCtx, arenaVisitor):
        self._battleCtx = battleCtx
        self._arenaVisitor = arenaVisitor
        self.init()

    def stopControl(self):
        self._battleCtx = None
        self._arenaVisitor = None
        self.stop()
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.AREA_MARKER

    def getPluginID(self):
        pass

    def spaceLoadCompleted(self):
        self.start()

    def _tickUpdate(self):
        super(AreaMarkersController, self)._tickUpdate()
        player = BigWorld.player()
        if player is None:
            return
        else:
            vehicle = player.getVehicleAttached()
            observableVehiclePosition = vehicle.position if vehicle else None
            for marker in self._markers.itervalues():
                if marker.isEmpty():
                    continue
                distanceToArea = marker.getDistanceToArea(observableVehiclePosition)
                if not self._isMarkerActuallyVisibleImpl(marker, distanceToArea):
                    marker.setVisible(False)
                    continue
                marker.setVisible(self._globalVisibility)
                marker.update(int(max(0, distanceToArea)))
                if self._prevGlobalVisibility != self._globalVisibility:
                    self._prevGlobalVisibility = self._globalVisibility
                    marker.setVisible(self._globalVisibility)
                if marker.isVisible:
                    marker.update(int(round(max(0, distanceToArea))))

            return

    def removeAllMarkers(self):
        for markerID in self.allMarkersID:
            self.removeMarker(markerID)

    def isMarkerActuallyVisible(self, marker):
        player = BigWorld.player()
        if player is None:
            return False
        else:
            vehicle = player.getVehicleAttached()
            observableVehiclePosition = vehicle.position if vehicle else None
            distanceToArea = marker.getDistanceToArea(observableVehiclePosition)
            return self._isMarkerActuallyVisibleImpl(marker, distanceToArea)

    def _isMarkerActuallyVisibleImpl(self, marker, distanceToArea):
        conditionDistance = marker.disappearingRadius
        if conditionDistance <= 0:
            return True
        else:
            isHidden = distanceToArea is None or (conditionDistance < distanceToArea if marker.reverseDisappearing else conditionDistance > distanceToArea)
            return not isHidden
