# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/accuracy_stacks_manager.py
from __future__ import absolute_import, division
import CGF
import SoundGroups
from cgf_components.vehicle_mechanics_components import AccuracyStacksRTPCComponent
from AccuracyStacksController import AccuracyStacksController

class AccuracyStacksMechanicSystem(CGF.System):
    AccuracyActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(AccuracyStacksRTPCComponent))
    AccuracyDeactivated = CGF.DeactivateReaction(CGF.ReactRw(AccuracyStacksRTPCComponent))
    AccuracyIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(AccuracyStacksRTPCComponent))
    AccuracyControllerAccess = CGF.AccessReaction(CGF.GameObject, CGF.Ro(AccuracyStacksController))
    Reactions = CGF.Reactions(AccuracyActivated, AccuracyDeactivated, AccuracyIterate, AccuracyControllerAccess)

    def commonUpdate(self):
        for accuracyStacksComponent in self.reaction(self.AccuracyDeactivated):
            self.onAccuracyStacksRTPCRemoved(accuracyStacksComponent)

        accuracyControllerAccess = self.reaction(self.AccuracyControllerAccess)
        for gameObject, accuracyStacksComponent in self.reaction(self.AccuracyActivated):
            self.onAccuracyStacksRTPCAdded(gameObject, accuracyStacksComponent, accuracyControllerAccess)

    def periodUpdate(self):
        accuracyControllerAccess = self.reaction(self.AccuracyControllerAccess)
        for accuracyStacksComponent in self.reaction(self.AccuracyIterate):
            self.onAccuracyStacksRTPCProcess(accuracyStacksComponent, accuracyControllerAccess)

    def onAccuracyStacksRTPCProcess(self, accuracyStacksComponent, accuracyControllerAccess):
        _, accuracyStacksController = accuracyControllerAccess.find(accuracyStacksComponent.controllerGO)
        self.__setAccuracyStacksRTPC(accuracyStacksComponent, accuracyStacksController)

    def onAccuracyStacksRTPCRemoved(self, accuracyStacksComponent):
        accuracyStacksComponent.controllerGO = None
        self.__setAccuracyStacksRTPC(accuracyStacksComponent, None)
        return

    def onAccuracyStacksRTPCAdded(self, gameObject, accuracyStacksComponent, accuracyControllerAccess):
        accuracyStacksComponent.controllerGO, comp = CGF.findParentWithReaction(gameObject, accuracyControllerAccess)
        self.__setAccuracyStacksRTPC(accuracyStacksComponent, comp)

    @classmethod
    def __setAccuracyStacksRTPC(cls, accuracyStacksComponent, accuracyStacksController):
        if accuracyStacksComponent.controllerGO is not None:
            progress = cls.__getAccuracyStacksProgress(accuracyStacksComponent.controllerGO, accuracyStacksController)
        else:
            progress = 0.0
        if accuracyStacksComponent.progress != progress:
            SoundGroups.g_instance.setGlobalRTPC(accuracyStacksComponent.RTPCName, progress)
            accuracyStacksComponent.progress = progress
        return

    @classmethod
    def __getAccuracyStacksProgress(cls, controllerGO, accuracyStacksController):
        if not controllerGO:
            return 0.0
        state = accuracyStacksController.getMechanicState()
        return 100 * (state.level + state.progress) / state.maxLevel
