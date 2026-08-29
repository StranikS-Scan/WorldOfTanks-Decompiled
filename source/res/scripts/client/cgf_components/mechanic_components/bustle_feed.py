# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/mechanic_components/bustle_feed.py
from __future__ import absolute_import
import CGF
from constants import IS_CLIENT
from cgf_modules.variable_components import VariableStorageComponent
if IS_CLIENT:
    from BustleFeedController import BustleFeedController
else:

    class BustleFeedController(object):
        pass


class BustleFeedVariableStorageCachingSystem(CGF.System):
    Activated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(BustleFeedController), CGF.Ro(VariableStorageComponent))
    Deactivated = CGF.DeactivateReaction(CGF.ReactRw(BustleFeedController), CGF.Ro(VariableStorageComponent))
    Reactions = CGF.Reactions(Deactivated, Activated)

    def update(self):
        for controller, _ in self.reaction(self.Deactivated):
            controller.setVariableStorageGO(None)

        for go, controller, _ in self.reaction(self.Activated):
            controller.setVariableStorageGO(go)

        return
