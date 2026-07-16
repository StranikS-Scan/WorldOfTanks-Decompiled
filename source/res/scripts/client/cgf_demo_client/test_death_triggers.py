# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/test_death_triggers.py
from __future__ import absolute_import
import logging
import CGF
import functools
from cgf_script.registration import ComponentProperty, registerComponent
from cgf_demo.demo_category import DEMO_CATEGORY
from DeathComponent import DeathComponent
from Triggers import AreaTriggerComponent
_logger = logging.getLogger(__name__)

@registerComponent
class TestAddDeathByTrigger(object):
    group = DEMO_CATEGORY
    editorTitle = 'Test Add Death by Trigger'
    domain = CGF.Domain.Client
    goLink = ComponentProperty(type=CGF.PropertyType.Link, editorName='goLink', value=CGF.GameObject)


@registerComponent
class TestRemoveDeathByTrigger(object):
    group = DEMO_CATEGORY
    editorTitle = 'Test Remove Death By Trigger'
    domain = CGF.Domain.Client
    goLink = ComponentProperty(type=CGF.PropertyType.Link, editorName='goLink', value=CGF.GameObject)


class TestDeathByTriggerSystem(CGF.System):
    AddDeathActivated = CGF.ActivateReaction(AreaTriggerComponent, CGF.ReactRo(TestAddDeathByTrigger))
    RemoveDeathActivated = CGF.ActivateReaction(AreaTriggerComponent, CGF.ReactRo(TestRemoveDeathByTrigger))
    DeathAccess = CGF.AccessReaction(CGF.Ro(DeathComponent))
    Reactions = CGF.Reactions(AddDeathActivated, RemoveDeathActivated, DeathAccess)

    def update(self):
        for trigger, removeDeath in self.reaction(self.RemoveDeathActivated):
            trigger.addEnterReaction(functools.partial(self.__removeDeath, removeDeath.goLink))

        for trigger, addDeath in self.reaction(self.AddDeathActivated):
            trigger.addEnterReaction(functools.partial(self.__addDeath, addDeath.goLink))

    def __addDeath(self, go):
        deathAccess = self.reaction(self.DeathAccess)
        if not deathAccess.find(go):
            q = CGF.CommandQueue(self.gom)
            q.createComponent(go, DeathComponent)

    def __removeDeath(self, go):
        deathAccess = self.reaction(self.DeathAccess)
        if deathAccess.find(go):
            q = CGF.CommandQueue(self.gom)
            q.removeComponent(go, DeathComponent)
