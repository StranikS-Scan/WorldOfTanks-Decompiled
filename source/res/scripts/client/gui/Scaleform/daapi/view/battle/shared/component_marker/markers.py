# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/component_marker/markers.py
import logging
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import World2DMarkerComponent, MinimapMarkerComponent, AnimationSequenceMarkerComponent, DirectionIndicatorMarkerComponent, ComponentBitMask, TerrainMarkerComponent
from ids_generators import SequenceIDGenerator
_logger = logging.getLogger(__name__)

class MarkerBase(object):
    _idGen = SequenceIDGenerator()
    COMPONENT_CLASS = {ComponentBitMask.MARKER_2D: World2DMarkerComponent,
     ComponentBitMask.MINIMAP_MARKER: MinimapMarkerComponent,
     ComponentBitMask.DIRECTION_INDICATOR: DirectionIndicatorMarkerComponent,
     ComponentBitMask.ANIM_SEQUENCE_MARKER: AnimationSequenceMarkerComponent,
     ComponentBitMask.TERRAIN_MARKER: TerrainMarkerComponent}

    def __init__(self, markerData):
        super(MarkerBase, self).__init__()
        self.__markerID = self._idGen.next()
        self._isVisible = markerData.get('visible', True)
        self._blockChangVisibility = not self._isVisible
        self._components = {}
        self._mask = markerData.get('bitMask', ComponentBitMask.NONE)
        self.__initComponents(markerData, self._mask)

    @property
    def mask(self):
        return self._mask

    @property
    def markerID(self):
        return self.__markerID

    @property
    def isVisible(self):
        return self._isVisible

    @property
    def blockChangVisibility(self):
        return self._blockChangVisibility

    @blockChangVisibility.setter
    def blockChangVisibility(self, value):
        self._blockChangVisibility = value

    def hasMarker2D(self):
        return self.mask & ComponentBitMask.MARKER_2D

    def hasMinimap(self):
        return self.mask & ComponentBitMask.MINIMAP_MARKER

    def getMarkerPosition(self):
        for component in self._components.itervalues():
            return component.position

        return None

    def isEmpty(self):
        return not self._components

    def addComponent(self, component):
        if component is None:
            _logger.error('addComponent: component is None')
        elif component.componentID in self._components:
            _logger.error('addComponent: component with the specified ID has already been added')
        else:
            self._components[component.componentID] = component
        return

    def getComponentByType(self, flag):
        return [ component for component in self._components.itervalues() if component.maskType == flag ]

    def update(self, *args, **kwargs):
        mask = kwargs.get('componentMaskType', ComponentBitMask.NONE)
        for component in self._components.itervalues():
            if not mask & component.maskType:
                component.update(*args, **kwargs)

    def clear(self):
        for component in self._components.itervalues():
            component.clear()

        self._components = {}

    def setVisible(self, isVisible):
        if self.blockChangVisibility:
            return
        self._isVisible = isVisible
        for component in self._components.itervalues():
            component.setVisible(self.isVisible)

    def attachGUI(self, guiProvider):
        for component in self._components.itervalues():
            component.attachGUI(guiProvider)

    def detachGUI(self):
        for component in self._components.itervalues():
            component.detachGUI()

    def setMatrix(self, matrix):
        for component in self._components.itervalues():
            component.setMarkerMatrix(matrix)

    def setEntity(self, entity):
        for component in self._components.itervalues():
            component.setMarkerEntity(entity)

    def __initComponents(self, markerData, markerBitMask):
        for flag in ComponentBitMask.LIST:
            if not flag & markerBitMask:
                continue
            componentConfigs = markerData.get(flag, [])
            for idx, componentConfig in enumerate(componentConfigs):
                clazz = componentConfig.get('clazz') or self.COMPONENT_CLASS.get(flag)
                if clazz:
                    self.addComponent(clazz(idx, markerData))


class AreaMarker(MarkerBase):

    def __init__(self, markerData):
        super(AreaMarker, self).__init__(markerData)
        self._disappearingRadius = markerData.get('disappearingRadius', 0.0)
        self._reverseDisappearing = markerData.get('reverseDisappearing', False)
        self._areaRadius = markerData.get('areaRadius', 0.0)

    @property
    def disappearingRadius(self):
        return self._disappearingRadius

    @property
    def reverseDisappearing(self):
        return self._reverseDisappearing

    @property
    def areaRadius(self):
        return self._areaRadius

    def getDistanceToArea(self, observableVehiclePosition):
        if observableVehiclePosition is None:
            return
        else:
            absDistance = (self.getMarkerPosition() - observableVehiclePosition).length
            distanceToArea = max(0, absDistance - self.areaRadius)
            return distanceToArea
