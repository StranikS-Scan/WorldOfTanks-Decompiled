# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTCaptureProgressComponent.py
import GenericComponents
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers import dependency
from constants import IS_VS_EDITOR
from skeletons.gui.battle_session import IBattleSessionProvider
if not IS_VS_EDITOR:
    from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import ComponentBitMask
MAX_PROGRESS = 100.0

class GeneratorCapturedComponent(object):

    def __init__(self, vehiclesIDs):
        super(GeneratorCapturedComponent, self).__init__()
        self.vehiclesIDs = vehiclesIDs


class WTCaptureProgressComponent(DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, *args, **kwargs):
        super(WTCaptureProgressComponent, self).__init__(*args, **kwargs)
        self.__marker = None
        self.__minimapMarker = None
        self.__generatorMarker = None
        return

    def set_activationProgress(self, prev):
        activation = self.activationProgress
        gameObject = self.entity.entityGameObject
        if activation.progress > 0:
            if activation.timeLeft <= 0 and activation.progress >= MAX_PROGRESS:
                if gameObject.findComponentByType(GeneratorCapturedComponent) is None:
                    gameObject.createComponent(GeneratorCapturedComponent, activation.invadersVehicleIDs)
            if self.__marker:
                if self.__generatorMarker:
                    self.__generatorMarker.onGeneratorCapture(self.__getIndex(), activation.progress, activation.timeLeft, activation.numInvaders)
                if self.__minimapMarker:
                    self.__minimapMarker.onGeneratorCapture(self.__getIndex(), activation.progress, activation.timeLeft, activation.numInvaders)
            ctrl = self.__guiSessionProvider.shared.feedback
            if ctrl:
                ctrl.onGeneratorCapture(self.__getIndex(), activation.progress, activation.timeLeft, activation.numInvaders)
            if gameObject.findComponentByType(GenericComponents.GeneratorProgressComponent) is None:
                gameObject.createComponent(GenericComponents.GeneratorProgressComponent, lambda : self.activationProgress.progress, lambda : self.activationProgress.timeLeft)
        elif prev is not None:
            self.__stopCapture()
            gameObject.removeComponentByType(GenericComponents.GeneratorProgressComponent)
        return

    def set_isCaptured(self, prev):
        ctrl = self.__guiSessionProvider.shared.feedback
        if ctrl and self.isCaptured:
            ctrl.onGeneratorStopCapture(self.__getIndex(), True)

    def _onAvatarReady(self):
        self.set_activationProgress(None)
        self.__marker = self.__fetchMarkerID()
        if self.__marker:
            self.__minimapMarker = self.__fetchMiniMapMarkerComponent(self.__marker)
            self.__generatorMarker = self.__fetchGeneratorMarkerComponent(self.__marker)
        return

    def __getIndex(self):
        return self.entity.wtIndex.index

    def __stopCapture(self):
        if self.__marker:
            self.__generatorMarker = self.__fetchGeneratorMarkerComponent(self.__marker)
            if self.__generatorMarker:
                self.__generatorMarker.onGeneratorStopCapture(self.__getIndex())
        if self.__minimapMarker:
            self.__minimapMarker.onGeneratorStopCapture(self.__getIndex())
        ctrl = self.__guiSessionProvider.shared.feedback
        if ctrl:
            ctrl.onGeneratorStopCapture(self.__getIndex(), False)

    def __fetchMarkerID(self):
        if 'entityMarker' in self.entity.dynamicComponents:
            ctrl = self.__guiSessionProvider.shared.areaMarker
            if ctrl:
                marker = ctrl.getMarkerById(self.entity.entityMarker.markerID)
                return marker
        return None

    def __fetchGeneratorMarkerComponent(self, marker):
        if marker.hasMarker2D():
            components = marker.getComponentByType(ComponentBitMask.MARKER_2D)
            if components:
                return components[0]
        return None

    def __fetchMiniMapMarkerComponent(self, marker):
        if marker.hasMinimap():
            components = marker.getComponentByType(ComponentBitMask.MINIMAP_MARKER)
            return components[0]
        else:
            return None
