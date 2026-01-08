# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/test_gun_effects_controller.py
import functools
import CGF
import Triggers
import Vehicular
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery
from cgf_events import gun_events
from constants import UNKNOWN_GUN_INDEX

@registerComponent
class TestEntranceSingleShot(object):
    category = DEMO_CATEGORY
    editorTitle = 'Test Entrance Single Shot'
    domain = CGF.DomainOption.DomainClient
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger to subscribe', value=Triggers.AreaTriggerComponent)
    gun = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Gun Installation', value=Vehicular.GunInstallationComponent)


class EntranceSingleShotManager(CGF.ComponentManager):

    @onAddedQuery(TestEntranceSingleShot)
    def onEntranceAdded(self, entrance):
        trigger = entrance.trigger()
        if trigger:
            trigger.addEnterReaction(functools.partial(self.__onEnter, entrance))

    def __onEnter(self, entrance, who, where):
        gunGO = entrance.gun.gameObject
        if gunGO is None or not gunGO.isValid():
            return
        else:
            spaceID = gunGO.spaceID
            gun_events.postVehicularSingleShotEvent(spaceID, gunGO.index, gunGO.name, UNKNOWN_GUN_INDEX)
            return


@registerComponent
class TestEntranceContinuousBurst(object):
    category = DEMO_CATEGORY
    editorTitle = 'Test Entrance Continuous Burst'
    domain = CGF.DomainOption.DomainClient
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger to subscribe', value=Triggers.AreaTriggerComponent)
    gun = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Gun Installation', value=Vehicular.GunInstallationComponent)


class EntranceContinuousBurstManager(CGF.ComponentManager):

    @onAddedQuery(TestEntranceContinuousBurst)
    def onEntranceAdded(self, entrance):
        trigger = entrance.trigger()
        if trigger:
            trigger.addEnterReaction(functools.partial(self.__onEnter, entrance))
            trigger.addExitReaction(functools.partial(self.__onExit, entrance))

    def __onEnter(self, entrance, who, where):
        gunGO = entrance.gun.gameObject
        if gunGO is None or not gunGO.isValid():
            return
        else:
            spaceID = gunGO.spaceID
            gun_events.postVehicularContinuousBurstEvent(spaceID, gunGO.index, gunGO.name, True)
            return

    def __onExit(self, entrance, who, where):
        gunGO = entrance.gun.gameObject
        if gunGO is None or not gunGO.isValid():
            return
        else:
            spaceID = gunGO.spaceID
            gun_events.postVehicularContinuousBurstEvent(spaceID, gunGO.index, gunGO.name, False)
            return
