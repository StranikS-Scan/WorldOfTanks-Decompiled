# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/entity_markers/markers_components.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import World2DLocationMarkerComponent, MinimapMarkerComponent, World2DMarkerComponent
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import ENTRY_SYMBOL_NAME
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import BASE_MARKER_MIN_SCALE, BASE_MARKER_BOUNDS, STATIC_MARKER_CULL_DISTANCE, BASE_MARKER_BOUND_MIN_SCALE, INNER_BASE_MARKER_BOUNDS
from gui.Scaleform.daapi.view.battle.shared.markers2d.markers import ReplyStateForMarker
from helpers import time_utils
from TeamBaseRecapturable import ITeamBasesRecapturableListener
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.genConsts.BATTLE_MINIMAP_CONSTS import BATTLE_MINIMAP_CONSTS
CAPTURE_POINTS_LIMIT = 100

class HWPickupPlacementMarkerComponent(World2DLocationMarkerComponent):
    _MIN_SCALE = 100.0
    _MIN_DISTANCE = 15

    @property
    def _symbol(self):
        pass

    def _setupMarker(self, gui):
        super(HWPickupPlacementMarkerComponent, self)._setupMarker(gui)
        self._setTimer(gui)

    def update(self, distance, *args, **kwargs):
        super(HWPickupPlacementMarkerComponent, self).update(distance, *args, **kwargs)
        gui = self._gui()
        self._setTimer(gui)

    def _setTimer(self, gui):
        if gui is not None:
            gui.invokeMarker(self._componentID, 'setIsSpawned', True)
            timeDeltaSec = self._entity.dropTime - BigWorld.serverTime()
            gui.invokeMarker(self._componentID, 'setTimer', time_utils.getTimeLeftFormat(timeDeltaSec))
        return


class HWPickupSpawnedMarkerComponent(World2DLocationMarkerComponent):
    _MIN_SCALE = 100.0
    _MIN_DISTANCE = 15

    @property
    def _symbol(self):
        pass

    def _setupMarker(self, gui):
        super(HWPickupSpawnedMarkerComponent, self)._setupMarker(gui)
        gui.invokeMarker(self._componentID, 'setIsSpawned', False)


class HWPickupPlacementMinimapMarkerComponent(MinimapMarkerComponent):

    def _setupMarker(self, gui):
        super(HWPickupPlacementMinimapMarkerComponent, self)._setupMarker(gui)
        gui.invoke(self._componentID, 'setIsSpawned', False)


class HWPickupSpawnedMinimapMarkerComponent(MinimapMarkerComponent):

    def _setupMarker(self, gui):
        super(HWPickupSpawnedMinimapMarkerComponent, self)._setupMarker(gui)
        gui.invoke(self._componentID, 'setIsSpawned', True)


class HWTeamBaseMarkersComponentBase(ITeamBasesRecapturableListener):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onBaseProgress(self, baseId, team, points, invadersCount, timeLeft):
        self._updateProgress(team, points)

    def onBaseCaptured(self, baseId, newTeam):
        self._updateTeamBaseStatus(True, 0.0)

    def onBaseCaptureStop(self, baseId):
        self._updateTeamBaseStatus()

    def onBaseTeamChanged(self, baseId, prevTeam, newTeam):
        self._updateTeamBaseStatus()

    def onBaseCaptureStart(self, baseId, team, isPlayerTeam, invadersCount, timeLeft):
        self._doCaptureStart(team)

    def onBaseInvadersTeamChanged(self, baseId, invadersTeam):
        self._updateTeamBaseStatus(points=0.0)

    def _convertTeam(self, team):
        if team == 0:
            return 'none'
        return 'ally' if team == self._playerTeam else 'enemy'

    def _updateProgress(self, team, points):
        normalizedPoints = points / CAPTURE_POINTS_LIMIT
        if team != 0:
            normalizedPoints = 1 - normalizedPoints
        normalizedPoints = max(normalizedPoints, 0.01)
        self._setCapturePoints(normalizedPoints)

    def _doCaptureStart(self, team):
        reverse = team != 0
        points = 0.999 if reverse else 0.0
        self._updateTeamBaseStatus(reverse, points)


class HWTeamBaseMarkerComponent(World2DMarkerComponent, HWTeamBaseMarkersComponentBase):

    @property
    def _symbol(self):
        pass

    def update(self, distance, *args, **kwargs):
        pass

    def attachGUI(self, guiProvider):
        super(HWTeamBaseMarkerComponent, self).attachGUI(guiProvider)
        self._entity.registerListener(self)

    def detachGUI(self):
        super(HWTeamBaseMarkerComponent, self).detachGUI()
        self._entity.unregisterListener(self)

    def _setupMarker(self, gui):
        self._playerTeam = self._sessionProvider.getArenaDP().getNumberOfTeam()
        owningTeam = self._convertTeam(self._entity.team)
        gui.invokeMarker(self._componentID, 'setTeamStatus', owningTeam, self._convertTeam(self._entity.invadersTeam))
        gui.invokeMarker(self._componentID, 'setIdentifier', self._entity.baseID)
        gui.invokeMarker(self._componentID, 'setActive', True)
        gui.setMarkerRenderInfo(self._componentID, BASE_MARKER_MIN_SCALE, BASE_MARKER_BOUNDS, INNER_BASE_MARKER_BOUNDS, STATIC_MARKER_CULL_DISTANCE, BASE_MARKER_BOUND_MIN_SCALE)
        gui.invokeMarker(self._componentID, 'setActiveState', ReplyStateForMarker.NO_ACTION.value)
        gui.setMarkerSticky(self._componentID, True)
        gui.invokeMarker(self._componentID, 'setIsEpicMarker', True)
        self._updateTeamBaseStatus()
        if self._entity.invadersCount > 0:
            self._doCaptureStart(self._entity.team)
            self._updateProgress(self._entity.team, self._entity.points)

    def _updateTeamBaseStatus(self, reverse=False, points=1.0):
        gui = self._gui()
        if gui is not None:
            gui.invokeMarker(self._componentID, 'setTeamStatus', self._convertTeam(self._entity.team), self._convertTeam(self._entity.team if reverse else self._entity.invadersTeam))
            gui.invokeMarker(self._componentID, 'setCapturePoints', points)
        return

    def _setCapturePoints(self, points):
        gui = self._gui()
        if gui is not None:
            gui.invokeMarker(self._componentID, 'setCapturePoints', points)
        return


class HWTeamBaseMinimapMarkerComponent(MinimapMarkerComponent, HWTeamBaseMarkersComponentBase):
    _CAPTURED_MARKER = ENTRY_SYMBOL_NAME.MARK_POSITION_HW

    def __init__(self, config, matrixProduct, isVisible=True):
        super(HWTeamBaseMinimapMarkerComponent, self).__init__(config, matrixProduct, isVisible)
        self._baseCapturedMarkerCreated = False
        self._baseCapturedMarkerID = self._idGen.next()

    def attachGUI(self, guiProvider):
        super(HWTeamBaseMinimapMarkerComponent, self).attachGUI(guiProvider)
        self._entity.registerListener(self)

    def detachGUI(self):
        super(HWTeamBaseMinimapMarkerComponent, self).detachGUI()
        self._entity.unregisterListener(self)

    def clear(self):
        self._deleteCapturedMarker()
        super(HWTeamBaseMinimapMarkerComponent, self).clear()

    def onBaseCaptured(self, baseId, newTeam):
        super(HWTeamBaseMinimapMarkerComponent, self).onBaseCaptured(baseId, newTeam)
        if newTeam == 0:
            return
        else:
            gui = self._gui()
            if gui is None:
                return
            self._deleteCapturedMarker()
            self._baseCapturedMarkerCreated = gui.createMarker(self._baseCapturedMarkerID, self._CAPTURED_MARKER, self._config.get('container', ''), matrix=self._matrixProduct, active=self._isVisible)
            return

    def _setupMarker(self, gui):
        super(HWTeamBaseMinimapMarkerComponent, self)._setupMarker(gui)
        self._playerTeam = self._sessionProvider.getArenaDP().getNumberOfTeam()
        gui.invoke(self._componentID, 'setTeamStatus', self._convertTeam(self._entity.team), self._convertTeam(self._entity.invadersTeam))
        gui.invoke(self._componentID, 'setIdentifier', self._entity.baseID)
        gui.invoke(self._componentID, BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_DEFAULT)
        self._updateTeamBaseStatus()
        if self._entity.invadersCount > 0:
            self._doCaptureStart(self._entity.team)
            self._updateProgress(self._entity.team, self._entity.points)

    def _deleteCapturedMarker(self):
        if self._baseCapturedMarkerCreated:
            gui = self._gui()
            if gui is not None:
                gui.deleteMarker(self._baseCapturedMarkerID)
                self._baseCapturedMarkerCreated = False
        return

    def _updateTeamBaseStatus(self, reverse=False, points=1.0):
        gui = self._gui()
        if gui is not None:
            gui.invoke(self._componentID, 'setTeamStatus', self._convertTeam(self._entity.team), self._convertTeam(self._entity.team if reverse else self._entity.invadersTeam))
            gui.invoke(self._componentID, 'setCapturePoints', points)
        return

    def _setCapturePoints(self, points):
        gui = self._gui()
        if gui is not None:
            gui.invoke(self._componentID, 'setCapturePoints', points)
        return
