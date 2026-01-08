# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/mechanic_components/cyclic_rocket/accelerator_status_tracker.py
import CGF
from StagedJetBoostersController import StagedJetBoostersController
from constants import AcceleratorStatus
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import autoregister, onProcessQuery, onRemovedQuery, onAddedQuery

@registerComponent
class AcceleratorStatusTrackerComponent(object):
    category = 'Vehicle Mechanics'
    editorTitle = 'Accelerator Status Tracker'
    domain = CGF.DomainOption.DomainClient
    target = ComponentProperty(CGFMetaTypes.LINK, editorName='Target GO', value=CGF.GameObject)
    type = ComponentProperty(CGFMetaTypes.INT, editorName='Type', value=AcceleratorStatus.NONE, annotations={'comboBox': {e.name:str(e.value) for e in AcceleratorStatus.__members__.values() if e != AcceleratorStatus.BOTH}})

    def __init__(self):
        self.status = AcceleratorStatus.NONE
        self.ctrl = None
        return


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class AcceleratorStatusTrackerComponentManager(CGF.ComponentManager):
    _TICK_RATE = 0.1

    @onAddedQuery(CGF.GameObject, AcceleratorStatusTrackerComponent)
    def onAdded(self, go, tracker):
        hierarchy = CGF.HierarchyManager(self.spaceID)
        if hierarchy is None:
            return
        else:
            res = hierarchy.findComponentInParent(go, StagedJetBoostersController)
            if res:
                tracker.ctrl = res[0]
            return

    @onRemovedQuery(AcceleratorStatusTrackerComponent)
    def onRemoved(self, tracker):
        self.__update(tracker.target, AcceleratorStatus.NONE, tracker.type)
        tracker.ctrl = None
        return

    @onProcessQuery(AcceleratorStatusTrackerComponent, tickGroup='preInitGroup', period=_TICK_RATE)
    def onProcess(self, tracker):
        if tracker.ctrl is None:
            return
        else:
            ctrl = tracker.ctrl.findComponentByType(StagedJetBoostersController)
            if ctrl is None:
                return
            status = ctrl.acceleratorStatus
            if status != tracker.status:
                self.__update(tracker.target, status, tracker.type)
                tracker.status = status
            return

    def __update(self, gameObject, status, flag):
        if gameObject is not None and gameObject.isValid():
            if status & flag:
                gameObject.activate()
            else:
                gameObject.deactivate()
        return
