# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/cgf_components/bunkers.py
from __future__ import absolute_import
from typing import Union
import CGF
from BunkerLogicComponent import BunkerLogicComponent

class BunkersSystem(CGF.System):
    BunkerLogicActivated = CGF.ActivateReaction(CGF.ReactRw(BunkerLogicComponent))
    BunkerLogicDeactivated = CGF.DeactivateReaction(CGF.ReactRw(BunkerLogicComponent))
    BunkerLogicIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.GameObject, CGF.Rw(BunkerLogicComponent), CGF.Ro(CGF.TransformComponent))
    Reactions = CGF.Reactions(BunkerLogicActivated, BunkerLogicDeactivated, BunkerLogicIterate)

    def update(self):
        for bunkerLogic in self.reaction(self.BunkerLogicDeactivated):
            bunkerLogic.stopLogic()

        for bunkerLogic in self.reaction(self.BunkerLogicActivated):
            bunkerLogic.startLogic(self.spaceID)

    def activeBunkersDirect(self):
        return self.reaction(self.BunkerLogicIterate)

    def findActiveBunkerDirect(self, entityID):
        for _, bunker, __ in self.reaction(self.BunkerLogicIterate):
            if bunker.destructibleEntityId == entityID:
                return bunker

        return None

    def findActiveBunkerLink(self, entityID):
        for go, bunker, _ in self.reaction(self.BunkerLogicIterate):
            if bunker.destructibleEntityId == entityID:
                return CGF.ComponentLink(go, BunkerLogicComponent)

        return CGF.ComponentLink()
