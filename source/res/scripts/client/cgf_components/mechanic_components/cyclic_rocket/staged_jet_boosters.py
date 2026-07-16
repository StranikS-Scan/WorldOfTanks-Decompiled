# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/mechanic_components/cyclic_rocket/staged_jet_boosters.py
from __future__ import absolute_import
import CGF
from StagedJetBoostersController import StagedJetBoostersController

class StagedJetBoostersComponentSystem(CGF.System):
    Activated = CGF.ActivateReaction(CGF.ReactRw(StagedJetBoostersController))
    Deactivated = CGF.DeactivateReaction(CGF.ReactRw(StagedJetBoostersController))
    Reactions = CGF.Reactions(Activated, Deactivated)

    def update(self):
        for controller in self.reaction(self.Deactivated):
            if controller.isValid and not controller.isComponentDestroyed():
                controller.detachInput()

        for controller in self.reaction(self.Activated):
            controller.attachInput()
            controller.createInputLogger()
