# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/test_gun_effects_controller.py
from __future__ import absolute_import
import CGF
import Triggers
import Vehicular
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.registration import ComponentProperty, registerComponent
from cgf_events import gun_events
from constants import UNKNOWN_GUN_INDEX

@registerComponent
class TestEntranceSingleShot(object):
    category = DEMO_CATEGORY
    editorTitle = 'Test Entrance Single Shot'
    domain = CGF.Domain.Client
    trigger = ComponentProperty(type=CGF.PropertyType.Link, editorName='AreaTrigger to subscribe', value=Triggers.AreaTriggerComponent)
    gun = ComponentProperty(type=CGF.PropertyType.Link, editorName='Gun Installation', value=Vehicular.GunInstallationComponent)


class EntranceSingleShotSystem(CGF.System):
    EntranceActivated = CGF.ActivateReaction(CGF.ReactRw(TestEntranceSingleShot))
    TriggerAccess = CGF.AccessReaction(CGF.Rw(Triggers.AreaTriggerComponent))
    EntranceAccess = CGF.AccessReaction(CGF.Rw(TestEntranceSingleShot))
    Reactions = CGF.Reactions(EntranceActivated, TriggerAccess, EntranceAccess)

    def update(self):
        triggerAccess = self.reaction(self.TriggerAccess)
        for entrance in self.reaction(self.EntranceActivated):
            trigger = triggerAccess.find(entrance.trigger)
            if trigger:
                trigger.addEnterReaction(self.__onEnter)

    def __onEnter(self, _, where):
        entranceAccess = self.reaction(self.EntranceAccess)
        entrance = entranceAccess.find(where)
        if not entrance:
            return
        gunGO = self.gom.gameObject(entrance.gun)
        if not gunGO.valid:
            return
        spaceID = gunGO.spaceID
        gun_events.postVehicularSingleShotEvent(spaceID, gunGO.index, gunGO.name, UNKNOWN_GUN_INDEX)


@registerComponent
class TestEntranceContinuousBurst(object):
    category = DEMO_CATEGORY
    editorTitle = 'Test Entrance Continuous Burst'
    domain = CGF.Domain.Client
    trigger = ComponentProperty(type=CGF.PropertyType.Link, editorName='AreaTrigger to subscribe', value=Triggers.AreaTriggerComponent)
    gun = ComponentProperty(type=CGF.PropertyType.Link, editorName='Gun Installation', value=Vehicular.GunInstallationComponent)


class EntranceContinuousBurstSystem(CGF.System):
    EntranceActivated = CGF.ActivateReaction(CGF.ReactRw(TestEntranceContinuousBurst))
    TriggerAccess = CGF.AccessReaction(CGF.Rw(Triggers.AreaTriggerComponent))
    EntranceAccess = CGF.AccessReaction(CGF.Rw(TestEntranceContinuousBurst))
    Reactions = CGF.Reactions(EntranceActivated, TriggerAccess, EntranceAccess)

    def update(self):
        triggerAccess = self.reaction(self.TriggerAccess)
        for entrance in self.reaction(self.EntranceActivated):
            trigger = triggerAccess.find(entrance.trigger)
            if trigger:
                trigger.addEnterReaction(self.__onEnter)
                trigger.addExitReaction(self.__onExit)

    def __onEnter(self, _, where):
        entranceAccess = self.reaction(self.EntranceAccess)
        entrance = entranceAccess.find(where)
        if not entrance:
            return
        gunGO = self.gom.gameObject(entrance.gun)
        if not gunGO.valid:
            return
        spaceID = gunGO.spaceID
        gun_events.postVehicularContinuousBurstEvent(spaceID, gunGO.index, gunGO.name, True)

    def __onExit(self, _, where):
        entranceAccess = self.reaction(self.EntranceAccess)
        entrance = entranceAccess.find(where)
        if not entrance:
            return
        gunGO = self.gom.gameObject(entrance.gun)
        if not gunGO.valid:
            return
        spaceID = gunGO.spaceID
        gun_events.postVehicularContinuousBurstEvent(spaceID, gunGO.index, gunGO.name, False)
