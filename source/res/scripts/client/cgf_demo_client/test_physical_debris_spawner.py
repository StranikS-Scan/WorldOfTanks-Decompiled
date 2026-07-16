# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/test_physical_debris_spawner.py
from __future__ import absolute_import
import functools
import CGF
import Triggers
import Physics
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.registration import ComponentProperty, registerComponent

@registerComponent
class TestEntranceSpawner(object):
    group = DEMO_CATEGORY
    editorTitle = 'Test Entrance Spawner'
    domain = CGF.Domain.Client
    trigger = ComponentProperty(type=CGF.PropertyType.Link, editorName='AreaTrigger to subscribe', value=Triggers.AreaTriggerComponent)
    debrisSpawner = ComponentProperty(type=CGF.PropertyType.Link, editorName='Spawner to subscribe', value=Physics.PhysicalDebrisSpawnerComponent)


class EntranceSpawnerSystem(CGF.System):
    EntranceSpawnerActivated = CGF.ActivateReaction(CGF.ReactRw(TestEntranceSpawner))
    AreaTriggerAccess = CGF.AccessReaction(CGF.Rw(Triggers.AreaTriggerComponent))
    DebrisSpawnerAccess = CGF.AccessReaction(CGF.Rw(Physics.PhysicalDebrisSpawnerComponent))
    Reactions = CGF.Reactions(EntranceSpawnerActivated, AreaTriggerAccess, DebrisSpawnerAccess)

    def update(self):
        triggerAccess = self.reaction(self.AreaTriggerAccess)
        for entrance in self.reaction(self.EntranceSpawnerActivated):
            self._onEntranceAdded(entrance, triggerAccess)

    def _onEntranceAdded(self, entrance, triggerAccess):
        trigger = triggerAccess.find(entrance.trigger)
        if trigger:
            debrisSpawner = entrance.debrisSpawner
            trigger.addEnterReaction(functools.partial(self.__onEnter, debrisSpawner))
            trigger.addExitReaction(functools.partial(self.__onExit, debrisSpawner))

    def __onEnter(self, debrisSpawnerUuid, who, where):
        debrisSpawnerAccess = self.reaction(self.DebrisSpawnerAccess)
        spawner = debrisSpawnerAccess.find(debrisSpawnerUuid)
        if spawner:
            spawner.spawnDebris()

    def __onExit(self, debrisSpawnerUuid, who, where):
        debrisSpawnerAccess = self.reaction(self.DebrisSpawnerAccess)
        spawner = debrisSpawnerAccess.find(debrisSpawnerUuid)
        if spawner:
            spawner.removeDebris()
