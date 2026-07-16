# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/mechanic_components/cyclic_rocket/nozzle_controller.py
from __future__ import absolute_import, division
import CGF
from GenericComponents import CyclicActivatorComponent
from constants import IS_EDITOR, PHASED_MECHANIC_STATE, AcceleratorStatus
from StagedJetBoostersController import StagedJetBoostersController
from cgf_script.registration import ComponentProperty, registerComponent

@registerComponent
class NozzleController(object):
    editorTitle = 'Nozzle Controller'
    category = 'Vehicle Mechanics'
    domain = CGF.Domain.ClientEditor
    activeStateGameObject = ComponentProperty(CGF.PropertyType.Link, editorName='activeStateGameObject', value=CGF.GameObject)
    endStateGameObject = ComponentProperty(CGF.PropertyType.Link, editorName='endStateGameObject', value=CGF.GameObject)
    failedStateGameObject = ComponentProperty(CGF.PropertyType.Link, editorName='failedStateGameObject', value=CGF.GameObject)
    boosterType = ComponentProperty(CGF.PropertyType.Int, editorName='boosterType', value=AcceleratorStatus.NONE, annotations={'comboBox': {e.name:str(e.value) for e in AcceleratorStatus.__members__.values() if e != AcceleratorStatus.BOTH}})

    def __init__(self):
        self.wasActive = False


@registerComponent
class NozzleActivationSyncComponent(object):
    editorTitle = 'Nozzle Activation Sync'
    category = 'Vehicle Mechanics'
    domain = CGF.Domain.ClientEditor
    endOffset = ComponentProperty(CGF.PropertyType.Float, editorName='endOffset', value=0.2)

    def __init__(self):
        self.endStateObjects = []


class NozzleControllerComponentSystem(CGF.System):
    Activated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(NozzleActivationSyncComponent), CGF.ReactRw(CyclicActivatorComponent))
    Deactivated = CGF.DeactivateReaction(CGF.ReactRw(NozzleActivationSyncComponent))
    NozzleActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(NozzleController))
    NozzleDeactivated = CGF.DeactivateReaction(CGF.ReactRw(NozzleController))
    BoosterAccess = CGF.AccessReaction(StagedJetBoostersController)
    NozzleControllerAccess = CGF.AccessReaction(NozzleController)
    Reactions = CGF.Reactions(Activated, Deactivated, NozzleActivated, BoosterAccess, NozzleControllerAccess, NozzleDeactivated)

    def update(self):
        queue = CGF.CommandQueue(self.gom)
        boosterAccess = self.reaction(self.BoosterAccess)
        nozzleAccess = self.reaction(self.NozzleControllerAccess)
        for nozzle in self.reaction(self.Deactivated):
            self.onRemovedSync(nozzle, queue)

        for nozzle in self.reaction(self.NozzleDeactivated):
            self.onRemovedNozzle(nozzle, queue)

        for go, nozzle in self.reaction(self.NozzleActivated):
            self.onAddedNozzle(go, nozzle, queue, boosterAccess)

        for go, nozzle, cyclic in self.reaction(self.Activated):
            self.onAddedSync(go, nozzle, cyclic, boosterAccess, nozzleAccess)

        queue.submit()

    def onAddedSync(self, go, sync, activator, boosterAccess, nozzleAccess):
        boosterCtrl = CGF.findParentWithReaction(go, boosterAccess)
        if boosterCtrl is None:
            return
        else:
            children = CGF.findInHierarchyWithReaction(go, nozzleAccess)
            sync.endStateObjects = []
            for ctrl in children:
                endState = self.gom.gameObject(ctrl.endStateGameObject)
                if endState is not None and endState.valid:
                    sync.endStateObjects.append(endState)

            state = boosterCtrl.getMechanicState()
            if state.state == PHASED_MECHANIC_STATE.ACTIVE:
                duration = state.duration - sync.endOffset
                activator.duration = duration / activator.loopCount
                activator.startOffset = duration - state.timeLeft
            return

    def onRemovedSync(self, sync, queue):
        for go in sync.endStateObjects:
            queue.deactivateGameObject(go)

        sync.endStateObjects = []

    def onAddedNozzle(self, go, nozzle, queue, boosterAccess):
        boosterCtrl = CGF.findParentWithReaction(go, boosterAccess)
        if boosterCtrl is None:
            return
        else:
            acceleratorStatus = boosterCtrl.acceleratorStatus if not IS_EDITOR else AcceleratorStatus.BOTH
            if acceleratorStatus & nozzle.boosterType:
                queue.activateGameObject(nozzle.activeStateGameObject)
                nozzle.wasActive = True
            else:
                queue.activateGameObject(nozzle.failedStateGameObject)
                nozzle.wasActive = False
            queue.deactivateGameObject(nozzle.endStateGameObject)
            return

    def onRemovedNozzle(self, nozzle, queue):
        if nozzle.wasActive:
            queue.activateGameObject(nozzle.endStateGameObject)
        nozzle.wasActive = False
        queue.deactivateGameObject(nozzle.activeStateGameObject)
        queue.deactivateGameObject(nozzle.failedStateGameObject)
