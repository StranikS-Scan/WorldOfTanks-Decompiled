# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Generator.py
import BigWorld
import GenericComponents
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
MAX_PROGRESS = 100.0

class GeneratorCapturedComponent(object):
    pass


class GeneratorActivationComponent(object):

    def __init__(self, genGO):
        super(GeneratorActivationComponent, self).__init__()
        self.generatorGO = genGO
        self.wasDamaged = False


class Generator(DynamicScriptComponent):

    def _onAvatarReady(self):
        self.set_activationProgress(None)
        return

    def set_activationProgress(self, prev):
        activation = self.activationProgress
        gameObject = self.entity.entityGameObject
        if activation.progress > 0:
            if activation.timeLeft <= 0 and activation.progress >= MAX_PROGRESS:
                if gameObject.findComponentByType(GeneratorCapturedComponent) is None:
                    gameObject.createComponent(GeneratorCapturedComponent)
            guiSessionProvider = dependency.instance(IBattleSessionProvider)
            ctrl = guiSessionProvider.shared.feedback
            if ctrl is not None:
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

    def onDestroy(self):
        super(Generator, self).onDestroy()
        self.__stopCapture()

    def __getIndex(self):
        return self.entity.entityInfo.index

    def __stopCapture(self):
        guiSessionProvider = dependency.instance(IBattleSessionProvider)
        ctrl = guiSessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onGeneratorStopCapture(self.__getIndex())
        return

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
