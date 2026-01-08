# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/mechanic_components/cyclic_rocket/nozzle_controller.py
import CGF
from GenericComponents import CyclicActivatorComponent
from cache import cached_property
from constants import IS_EDITOR, PHASED_MECHANIC_STATE, AcceleratorStatus
from StagedJetBoostersController import StagedJetBoostersController
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery

@registerComponent
class NozzleController(object):
    editorTitle = 'Nozzle Controller'
    category = 'Vehicle Mechanics'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    activeStateGameObject = ComponentProperty(CGFMetaTypes.LINK, editorName='activeStateGameObject', value=CGF.GameObject)
    endStateGameObject = ComponentProperty(CGFMetaTypes.LINK, editorName='endStateGameObject', value=CGF.GameObject)
    failedStateGameObject = ComponentProperty(CGFMetaTypes.LINK, editorName='failedStateGameObject', value=CGF.GameObject)
    boosterType = ComponentProperty(CGFMetaTypes.INT, editorName='boosterType', value=AcceleratorStatus.NONE, annotations={'comboBox': {e.name:str(e.value) for e in AcceleratorStatus.__members__.values() if e != AcceleratorStatus.BOTH}})

    def __init__(self):
        self.wasActive = False


@registerComponent
class NozzleActivationSyncComponent(object):
    editorTitle = 'Nozzle Activation Sync'
    category = 'Vehicle Mechanics'
    domain = CGF.DomainOption.DomainClient
    endOffset = ComponentProperty(CGFMetaTypes.FLOAT, editorName='endOffset', value=0.2)

    def __init__(self):
        self.endStateObjects = []


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
class NozzleControllerComponentManager(CGF.ComponentManager):

    @cached_property
    def __hierarchy(self):
        hierarchyManager = CGF.HierarchyManager(self.spaceID)
        return hierarchyManager

    @onAddedQuery(CGF.GameObject, NozzleActivationSyncComponent, CyclicActivatorComponent, tickGroup='preInitGroup')
    def onAddedSync(self, go, sync, activator):
        hierarchy = self.__hierarchy
        if hierarchy is None:
            return
        else:
            res = hierarchy.findComponentInParent(go, StagedJetBoostersController)
            if not res:
                return
            boosterCtrl = res[1]
            children = hierarchy.findComponentsInHierarchy(go, NozzleController)
            sync.endStateObjects = []
            for _, ctrl in children:
                endState = ctrl.endStateGameObject
                if endState is not None and endState.isValid():
                    sync.endStateObjects.append(endState)

            state = boosterCtrl.getMechanicState()
            if state.state == PHASED_MECHANIC_STATE.ACTIVE:
                duration = state.duration - sync.endOffset
                activator.duration = duration / activator.loopCount
                activator.startOffset = duration - state.timeLeft
            return

    @onRemovedQuery(NozzleActivationSyncComponent, tickGroup='preInitGroup')
    def onRemovedSync(self, sync):
        for go in sync.endStateObjects:
            go.deactivate()

        sync.endStateObjects = []

    @onAddedQuery(CGF.GameObject, NozzleController, tickGroup='preInitGroup')
    def onAddedNozzle(self, go, nozzle):
        hierarchy = self.__hierarchy
        if hierarchy is None:
            return
        else:
            res = hierarchy.findComponentInParent(go, StagedJetBoostersController)
            if not res:
                return
            boosterCtrl = res[1]
            acceleratorStatus = boosterCtrl.acceleratorStatus if not IS_EDITOR else AcceleratorStatus.BOTH
            if acceleratorStatus & nozzle.boosterType:
                self.__activate(nozzle.activeStateGameObject)
                nozzle.wasActive = True
            else:
                self.__activate(nozzle.failedStateGameObject)
                nozzle.wasActive = False
            self.__deactivate(nozzle.endStateGameObject)
            return

    @onRemovedQuery(NozzleController)
    def onRemovedNozzle(self, nozzle):
        if nozzle.wasActive:
            self.__activate(nozzle.endStateGameObject)
        nozzle.wasActive = False
        self.__deactivate(nozzle.activeStateGameObject)
        self.__deactivate(nozzle.failedStateGameObject)

    def __activate(self, link):
        if link is not None and link.isValid():
            link.activate()
        return

    def __deactivate(self, link):
        if link is not None and link.isValid():
            link.deactivate()
        return
