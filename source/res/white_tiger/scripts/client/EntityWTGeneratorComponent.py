# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/EntityWTGeneratorComponent.py
import BigWorld
import GenericComponents
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import IS_VS_EDITOR
if not IS_VS_EDITOR:
    from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import ComponentBitMask
MAX_PROGRESS = 100.0

class GeneratorCapturedComponent(object):

    def __init__(self, vehiclesIDs):
        super(GeneratorCapturedComponent, self).__init__()
        self.vehiclesIDs = vehiclesIDs


class GeneratorActivationComponent(object):

    def __init__(self, genGO):
        super(GeneratorActivationComponent, self).__init__()
        self.generatorGO = genGO
        self.wasDamaged = False


class EntityWTGeneratorComponent(DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, *args, **kwargs):
        super(EntityWTGeneratorComponent, self).__init__(*args, **kwargs)
        self.__marker = None
        return

    def _onAvatarReady(self):
        self.set_activationProgress(None)
        self.__marker = self.__fetchMarkerID()
        if self.__marker:
            self.__minimapMarker = self.__fetchMiniMapMarkerComponent(self.__marker)
            self.__generatorMarker = self.__fetchGeneratorMarkerComponent(self.__marker)
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
            if prev is None:
                self.activationAdd(activation.invadersVehicleIDs)
            elif activation.numInvaders != prev.numInvaders:
                self.activationRemove(frozenset(prev.invadersVehicleIDs).difference(activation.invadersVehicleIDs))
                self.activationAdd(frozenset(activation.invadersVehicleIDs).difference(prev.invadersVehicleIDs))
            elif prev.progress > activation.progress:
                self.updateFirstDamaged(activation.invadersVehicleIDs)
        elif prev is not None:
            self.__stopCapture()
            self.activationRemove(prev.invadersVehicleIDs)
            gameObject.removeComponentByType(GenericComponents.GeneratorProgressComponent)
        return

    def capture(self):
        ctrl = self.__guiSessionProvider.shared.feedback
        if ctrl:
            ctrl.onGeneratorStopCapture(self.__getIndex(), True)

    def onDestroy(self):
        super(EntityWTGeneratorComponent, self).onDestroy()
        self.__stopCapture()

    def __getIndex(self):
        return self.entity.indexPool.index

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

    def updateFirstDamaged(self, vIds):
        for veh in [ BigWorld.entities[vId] for vId in vIds if BigWorld.entities.has_key(vId) ]:
            activation = veh.entityGameObject.findComponentByType(GeneratorActivationComponent)
            if activation and activation.wasDamaged:
                self.activationRemove([veh.id])
                self.activationAdd([veh.id])
                return

    def activationAdd(self, added):
        gameObject = self.entity.entityGameObject
        for veh in [ BigWorld.entities[vId] for vId in added if BigWorld.entities.has_key(vId) ]:
            veh.entityGameObject.createComponent(GeneratorActivationComponent, gameObject)

    def activationRemove(self, removed):
        for veh in [ BigWorld.entities[vId] for vId in removed if BigWorld.entities.has_key(vId) ]:
            veh.entityGameObject.removeComponentByType(GeneratorActivationComponent)

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
