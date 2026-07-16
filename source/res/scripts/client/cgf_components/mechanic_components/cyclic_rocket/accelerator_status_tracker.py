# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/mechanic_components/cyclic_rocket/accelerator_status_tracker.py
from __future__ import absolute_import
import CGF
from StagedJetBoostersController import StagedJetBoostersController
from constants import AcceleratorStatus
from cgf_script.registration import ComponentProperty, registerComponent

@registerComponent
class AcceleratorStatusTrackerComponent(object):
    category = 'Vehicle Mechanics'
    editorTitle = 'Accelerator Status Tracker'
    domain = CGF.Domain.Client
    target = ComponentProperty(CGF.PropertyType.Link, editorName='Target GO', value=CGF.GameObject)
    type = ComponentProperty(CGF.PropertyType.Int, editorName='Type', value=AcceleratorStatus.NONE, annotations={'comboBox': {e.name:str(e.value) for e in AcceleratorStatus.__members__.values() if e != AcceleratorStatus.BOTH}})

    def __init__(self):
        self.status = AcceleratorStatus.NONE
        self.ctrl = None
        return


class AcceleratorStatusTrackerComponentSystem(CGF.System):
    Activated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(AcceleratorStatusTrackerComponent))
    Deactivated = CGF.DeactivateReaction(CGF.ReactRw(AcceleratorStatusTrackerComponent))
    Iterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(AcceleratorStatusTrackerComponent))
    BoosterAccess = CGF.AccessReaction(CGF.GameObject, CGF.Ro(StagedJetBoostersController))
    Reactions = CGF.Reactions(Activated, Deactivated, Iterate, BoosterAccess)

    def commonUpdate(self):
        boosterAccess = self.reaction(self.BoosterAccess)
        queue = CGF.CommandQueue(self.spaceID)
        for status in self.reaction(self.Deactivated):
            self.onRemoved(status, queue)

        for go, status in self.reaction(self.Activated):
            self.onAdded(go, status, boosterAccess)

        queue.submit()

    def periodUpdate(self):
        boosterAccess = self.reaction(self.BoosterAccess)
        queue = CGF.CommandQueue(self.spaceID)
        for status in self.reaction(self.Iterate):
            self.onProcess(status, boosterAccess, queue)

        queue.submit()

    def onAdded(self, go, tracker, boosterAccess):
        boosterAccessor = CGF.findParentWithReaction(go, boosterAccess)
        if boosterAccessor is not None:
            tracker.ctrl, _ = boosterAccessor
        return

    def onRemoved(self, tracker, queue):
        self.__update(tracker.target, AcceleratorStatus.NONE, tracker.type, queue)
        tracker.ctrl = None
        return

    def onProcess(self, tracker, boosterAccess, queue):
        if tracker.ctrl is None:
            return
        else:
            _, ctrl = boosterAccess.find(tracker.ctrl)
            if ctrl is None:
                return
            status = ctrl.acceleratorStatus
            if status != tracker.status:
                self.__update(tracker.target, status, tracker.type, queue)
                tracker.status = status
            return

    def __update(self, tracker, status, flag, queue):
        gameObject = self.gom.gameObject(tracker)
        if gameObject is not None and gameObject.valid:
            if status & flag:
                queue.activateGameObject(gameObject)
            else:
                queue.deactivateGameObject(gameObject)
        return
