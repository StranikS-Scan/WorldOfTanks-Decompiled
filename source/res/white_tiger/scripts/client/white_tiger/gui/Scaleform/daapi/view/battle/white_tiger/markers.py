# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/markers.py
import Math
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import MinimapMarkerComponent, World2DMarkerComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class World2DLocationMarkerComponent(World2DMarkerComponent):
    _CULL_DISTANCE = 1800
    _MIN_SCALE = 50.0
    _BOUNDS = Math.Vector4(30, 30, 90, -15)
    _INNER_BOUNDS = Math.Vector4(15, 15, 70, -35)
    _BOUNDS_MIN_SCALE = Math.Vector2(1.0, 0.8)
    _MIN_DISTANCE = 18
    _MAX_CAPTURE_PROGRESS = 100

    def __init__(self, idx, data):
        super(World2DLocationMarkerComponent, self).__init__(idx, data)
        self._createMarker()
        self._minDistance = self._MIN_DISTANCE
        self._config = data.get(self.maskType)[idx]
        self._distance = self._config.get('distance', 0)
        self._isSticky = self._config.get('isSticky', False)

    def setVisible(self, isVisible):
        super(World2DLocationMarkerComponent, self).setVisible(isVisible and self._getActualVisibility())

    def update(self, distance, *args, **kwargs):
        super(World2DLocationMarkerComponent, self).update(distance)
        if self._distance != distance:
            self._distance = distance

    def _getActualVisibility(self):
        return self._distance >= self._minDistance


class World2DIndexedMarkerComponent(World2DLocationMarkerComponent):
    _DEFAULT_ALPHA = 1.0
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, idx, data):
        super(World2DIndexedMarkerComponent, self).__init__(idx, data)
        self._isFirstShow = True

    def _createMarker(self):
        super(World2DIndexedMarkerComponent, self)._createMarker()
        gui = self._gui()
        if gui:
            alpha = self.getAlpha()
            gui.mapCustomEntityID(self._componentID, self._entityIndex)
            gui.invokeMarker(self._componentID, 'setEntityIndex', self._entityIndex)
            gui.invokeMarker(self._componentID, 'setAlpha', alpha)
            gui.setMarkerSticky(self._componentID, self._isSticky)
            minScale = self._config.get('minScale', self._MIN_SCALE)
            gui.setMarkerRenderInfo(self._componentID, minScale, self._BOUNDS, self._INNER_BOUNDS, self._CULL_DISTANCE, self._BOUNDS_MIN_SCALE)
            gui.setMarkerBoundEnabled(self._componentID, True)
            ctrl = self.sessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.onAddCommandReceived += self.__onAddCommandReceived
        return

    def _deleteMarker(self):
        gui = self._gui()
        if gui:
            gui.deleteCustomEntityID(self._componentID)
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onAddCommandReceived -= self.__onAddCommandReceived
        super(World2DIndexedMarkerComponent, self)._deleteMarker()
        return

    @property
    def _entityIndex(self):
        return self._entity.indexPool.index if self._entity and 'indexPool' in self._entity.dynamicComponents else 0

    def getAlpha(self):
        return self._config.get('alpha', self._DEFAULT_ALPHA)

    def __onAddCommandReceived(self, addedID, markerType):
        gui = self._gui()
        if gui:
            markerID = gui.getMarkerIdFormEntityID(addedID)
            if markerID == self._componentID:
                gui.invokeMarker(markerID, 'playAnimation')


class World2DGeneratorMarkerComponentOn(World2DIndexedMarkerComponent):

    def __init__(self, idx, data):
        super(World2DGeneratorMarkerComponentOn, self).__init__(idx, data)
        self.__lastProgressValue = 0

    def _createMarker(self):
        super(World2DGeneratorMarkerComponentOn, self)._createMarker()
        gui = self._gui()
        if gui and self.__lastProgressValue > 0:
            gui.invokeMarker(self._componentID, 'setMarkerProgress', self.__lastProgressValue)

    def onGeneratorCapture(self, generatorIndex, progress, timeLeft, numInvaders):
        gui = self._gui()
        if gui:
            if generatorIndex == self._entityIndex:
                gui.invokeMarker(self._componentID, 'setMarkerProgress', progress)
                self.__lastProgressValue = progress

    def onGeneratorStopCapture(self, generatorIndex):
        gui = self._gui()
        if generatorIndex == self._entityIndex:
            gui.invokeMarker(self._componentID, 'resetGeneratorMarker')
            self.__lastProgressValue = 0


class World2DGeneratorMarkerComponentOff(World2DIndexedMarkerComponent):

    def _createMarker(self):
        super(World2DGeneratorMarkerComponentOff, self)._createMarker()
        gui = self._gui()
        if gui:
            alpha = self.getAlpha()
            gui.invokeMarker(self._componentID, 'setAlpha', alpha)


class MinimapIndexedMarkerComponent(MinimapMarkerComponent):
    _DEFAULT_ALPHA = 0.5
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, idx, data):
        super(MinimapIndexedMarkerComponent, self).__init__(idx, data)
        self._minimapData = data.get(self.maskType)[idx]

    @property
    def _entityIndex(self):
        return self._entity.indexPool.index if self._entity and 'indexPool' in self._entity.dynamicComponents else 0

    def _createMarker(self):
        super(MinimapIndexedMarkerComponent, self)._createMarker()
        gui = self._gui()
        if gui:
            alpha = self.getAlpha()
            gui.mapCustomEntityID(self._componentID, self._entityIndex)
            gui.invoke(self._componentID, 'setEntityIndex', self._entityIndex)
            gui.invoke(self._componentID, 'setAlpha', alpha)
            gui.invoke(self._componentID, 'setGeneratorProgress', 0)
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onAddCommandReceived += self.__onAddCommandReceived
        return

    def _deleteMarker(self):
        gui = self._gui()
        if gui:
            gui.deleteCustomEntityID(self._componentID)
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onAddCommandReceived -= self.__onAddCommandReceived
        super(MinimapIndexedMarkerComponent, self)._deleteMarker()
        return

    def getAlpha(self):
        return self._minimapData.get('alpha', self._DEFAULT_ALPHA)

    def __onAddCommandReceived(self, addedID, markerType):
        gui = self._gui()
        if gui:
            markerID = gui.getMarkerIdFormEntityID(addedID)
            if markerID == self._componentID:
                gui.invoke(markerID, 'playAnimation')


class MinimapGeneratorMarkerComponentOn(MinimapIndexedMarkerComponent):

    def onGeneratorCapture(self, generatorIndex, progress, timeLeft, numInvaders):
        gui = self._gui()
        if gui:
            if generatorIndex == self._entityIndex:
                gui.invoke(self._componentID, 'setGeneratorProgress', progress)

    def onGeneratorStopCapture(self, generatorIndex):
        gui = self._gui()
        if gui:
            gui.invoke(self._componentID, 'resetGeneratorMarker')


class MinimapGeneratorMarkerComponentOff(MinimapIndexedMarkerComponent):

    def _createMarker(self):
        super(MinimapGeneratorMarkerComponentOff, self)._createMarker()
        gui = self._gui()
        if gui:
            alpha = self.getAlpha()
            gui.invoke(self._componentID, 'setAlpha', alpha)
