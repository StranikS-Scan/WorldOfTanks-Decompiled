# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/markers.py
import Math
from cgf_components.wt_helpers import isBoss
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import MinimapMarkerComponent, World2DMarkerComponent
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import EventKeys
from gui.wt_event.wt_event_helpers import getSpeed
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class World2DLocationMarkerComponent(World2DMarkerComponent):
    _CULL_DISTANCE = 1800
    _MIN_SCALE = 50.0
    _BOUNDS = Math.Vector4(30, 30, 90, -15)
    _INNER_BOUNDS = Math.Vector4(15, 15, 70, -35)
    _BOUNDS_MIN_SCALE = Math.Vector2(1.0, 0.8)
    _MIN_Y_OFFSET = 1.2
    _MAX_Y_OFFSET = 3.2
    _DISTANCE_FOR_MIN_Y_OFFSET = 400
    _MAX_Y_BOOST = 1.4
    _BOOST_START = 120
    _MIN_DISTANCE = 50

    def __init__(self, config, matrixProduct, isVisible=True):
        super(World2DLocationMarkerComponent, self).__init__(config, matrixProduct, isVisible)
        self._minDistance = self._config.get('minDistance', self._MIN_DISTANCE)

    @property
    def _symbol(self):
        pass

    def update(self, distance, *args, **kwargs):
        if self._distance != distance:
            self._distance = distance
            self._onDistanceChanged()
        self.setVisible(self._getActualVisibility())

    def _getActualVisibility(self):
        return self._distance >= self._minDistance

    def _onDistanceChanged(self):
        pass

    def _setupMarker(self, gui):
        gui.setMarkerSticky(self._componentID, self._config.get('isSticky', False))
        minScale = self._config.get('minScale', self._MIN_SCALE)
        gui.setMarkerRenderInfo(self._componentID, minScale, self._BOUNDS, self._INNER_BOUNDS, self._CULL_DISTANCE, self._BOUNDS_MIN_SCALE)
        gui.setMarkerLocationOffset(self._componentID, self._MIN_Y_OFFSET, self._MAX_Y_OFFSET, self._DISTANCE_FOR_MIN_Y_OFFSET, self._MAX_Y_BOOST, self._BOOST_START)


class World2DIndexedMarkerComponent(World2DLocationMarkerComponent):
    _DEFAULT_ALPHA = 1.0

    def __init__(self, config, matrixProduct, isVisible=True):
        super(World2DIndexedMarkerComponent, self).__init__(config, matrixProduct, isVisible)
        self._isFirstShow = True

    def _onDistanceChanged(self):
        gui = self._gui()
        if self._isVisible and self._isMarkerExists and gui:
            gui.invokeMarker(self._componentID, 'setDistance', self._distance)

    @property
    def _entityIndex(self):
        return self._entity.entityInfo.index if self._entity and 'entityInfo' in self._entity.dynamicComponents else 0

    def getAlpha(self):
        return self._config.get('alpha', self._DEFAULT_ALPHA)

    def _setupMarker(self, gui):
        super(World2DIndexedMarkerComponent, self)._setupMarker(gui)
        gui.invokeMarker(self._componentID, 'setEntityIndex', self._entityIndex)
        alpha = self.getAlpha()
        gui.invokeMarker(self._componentID, 'setAlpha', alpha)
        gui.invokeMarker(self._componentID, 'setDistance', self._distance)
        if self._isFirstShow:
            self._isFirstShow = False
            if alpha == self._DEFAULT_ALPHA:
                gui.invokeMarker(self._componentID, 'playAnimation')


class World2DFollowerMarkerComponent(World2DIndexedMarkerComponent):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, config, matrixProduct, isVisible=True):
        super(World2DFollowerMarkerComponent, self).__init__(config, matrixProduct, isVisible)
        self._playerBombID = 0

    def attachGUI(self, guiProvider):
        super(World2DFollowerMarkerComponent, self).attachGUI(guiProvider)
        if self._bombCtrl:
            self._bombCtrl.onBombUpdated += self._onBombUpdated

    def detachGUI(self):
        if self._bombCtrl:
            self._bombCtrl.onBombUpdated -= self._onBombUpdated
        super(World2DFollowerMarkerComponent, self).detachGUI()

    def _setupMarker(self, gui):
        super(World2DFollowerMarkerComponent, self)._setupMarker(gui)
        playerVehicleInfo = self._sessionProvider.getArenaDP().getVehicleInfo()
        playerBombID = playerVehicleInfo.gameModeSpecific.getValue(EventKeys.BOMB_INDEX.value)
        self._setPlayerBomb(playerBombID)

    def _onBombUpdated(self, vehicleID, params):
        playerBombID = params.timerID if avatar_getter.getPlayerVehicleID() == vehicleID else 0
        self._setPlayerBomb(playerBombID)

    def _setPlayerBomb(self, bombID):
        if self._playerBombID != bombID:
            self._playerBombID = bombID
            self._onPlayerBombChanged()

    def _onPlayerBombChanged(self):
        pass

    @property
    def _bombCtrl(self):
        return self._sessionProvider.dynamic.playersPanel


class World2DCampMarkerComponent(World2DFollowerMarkerComponent):
    _BOMB_FOLLOWER_ALPHA = 0.5

    def getAlpha(self):
        return self._BOMB_FOLLOWER_ALPHA if self._playerBombID else super(World2DCampMarkerComponent, self).getAlpha()

    def _onPlayerBombChanged(self):
        gui = self._gui()
        if self._isVisible and gui:
            if self._playerBombID:
                gui.invokeMarker(self._componentID, 'stopAnimation')
            gui.invokeMarker(self._componentID, 'setAlpha', self.getAlpha())

    @property
    def _symbol(self):
        return 'AllyCampLocationMarkerUI' if isBoss() else 'EnemyCampLocationMarkerUI'


class World2DGeneratorMarkerComponent(World2DFollowerMarkerComponent):

    @property
    def _symbol(self):
        pass

    def _onPlayerBombChanged(self):
        gui = self._gui()
        if self._isVisible and gui and self.getAlpha() == self._DEFAULT_ALPHA:
            method = 'playRepeatingAnimation' if self._playerBombID else 'stopAnimation'
            gui.invokeMarker(self._componentID, method)


class World2DBombMarkerComponent(World2DFollowerMarkerComponent):

    def __init__(self, config, matrixProduct, isVisible=True):
        super(World2DBombMarkerComponent, self).__init__(config, matrixProduct, isVisible)
        self.__isBombPaused = False

    @property
    def _symbol(self):
        pass

    @property
    def _followeeID(self):
        return self._entity.follower.followeeID if self._entity and 'follower' in self._entity.dynamicComponents else None

    def _getActualVisibility(self):
        return self._playerBombID != self._entity.id and not self.__isBombPaused

    def _setupMarker(self, gui):
        super(World2DBombMarkerComponent, self)._setupMarker(gui)
        stressTimer = self._entity.dynamicComponents.get('stressTimer')
        if stressTimer:
            timeLeft = int(round(stressTimer.timeToDelete))
            timeTotal = stressTimer.lifetime
            playbackSpeed = 0 if stressTimer.isPaused else getSpeed() * stressTimer.timerInfo.factor
            gui.invokeMarker(self._componentID, 'setBombTimer', timeLeft, timeTotal, playbackSpeed)
            gui.invokeMarker(self._componentID, 'setIsCaptured', bool(self._followeeID))

    def _onBombUpdated(self, vehicleID, params):
        if params.timerID != self._entity.id:
            return
        super(World2DBombMarkerComponent, self)._onBombUpdated(vehicleID, params)
        self.__isBombPaused = params.isPaused
        self.setVisible(self._getActualVisibility())
        gui = self._gui()
        if self._isVisible and gui:
            playbackSpeed = 0 if params.isPaused else getSpeed() * params.factor
            gui.invokeMarker(self._componentID, 'setBombTimer', params.leftTime, params.totalTime, playbackSpeed)
            gui.invokeMarker(self._componentID, 'setIsCaptured', bool(vehicleID))


class MinimapIndexedMarkerComponent(MinimapMarkerComponent):

    @property
    def _entityIndex(self):
        return self._entity.entityInfo.index if self._entity and 'entityInfo' in self._entity.dynamicComponents else 0

    def _setupMarker(self, gui):
        gui.invoke(self._componentID, 'setEntityIndex', self._entityIndex)


class MinimapCampMarkerComponent(MinimapIndexedMarkerComponent):

    def _setupMarker(self, gui):
        super(MinimapCampMarkerComponent, self)._setupMarker(gui)
        gui.invoke(self._componentID, 'setIsAlly', isBoss())


class MinimapGeneratorMarkerComponent(MinimapIndexedMarkerComponent):

    def _setupMarker(self, gui):
        super(MinimapGeneratorMarkerComponent, self)._setupMarker(gui)
        gui.invoke(self._componentID, 'setAlpha', self._config.get('alpha', 1.0))


class MinimapBombMarkerComponent(MinimapIndexedMarkerComponent):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def attachGUI(self, guiProvider):
        super(MinimapBombMarkerComponent, self).attachGUI(guiProvider)
        if self._bombCtrl:
            self._bombCtrl.onBombUpdated += self._onBombUpdated

    def detachGUI(self):
        if self._bombCtrl:
            self._bombCtrl.onBombUpdated -= self._onBombUpdated
        super(MinimapBombMarkerComponent, self).detachGUI()

    def _setupMarker(self, gui):
        super(MinimapBombMarkerComponent, self)._setupMarker(gui)
        stressTimer = self._entity.dynamicComponents.get('stressTimer')
        if stressTimer:
            timeLeft = int(round(stressTimer.timeToDelete))
            timeTotal = stressTimer.lifetime
            playbackSpeed = 0 if stressTimer.isPaused else getSpeed() * stressTimer.timerInfo.factor
            gui.invoke(self._componentID, 'setBombTimer', timeLeft, timeTotal, playbackSpeed)
            gui.invoke(self._componentID, 'setIsCaptured', bool(self._followeeID))

    def _onBombUpdated(self, vehicleID, params):
        if params.timerID != self._entity.id:
            return
        gui = self._gui()
        self.setVisible(not avatar_getter.getPlayerVehicleID() == vehicleID)
        if self._isVisible and gui:
            playbackSpeed = 0 if params.isPaused else getSpeed() * params.factor
            gui.invoke(self._componentID, 'setBombTimer', params.leftTime, params.totalTime, playbackSpeed)
            gui.invoke(self._componentID, 'setIsCaptured', bool(vehicleID))

    @property
    def _bombCtrl(self):
        return self._sessionProvider.dynamic.playersPanel

    @property
    def _followeeID(self):
        return self._entity.follower.followeeID if self._entity and 'follower' in self._entity.dynamicComponents else None
