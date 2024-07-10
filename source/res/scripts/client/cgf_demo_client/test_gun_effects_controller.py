# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/test_gun_effects_controller.py
import functools
import CGF
import Triggers
import Vehicular
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery

@registerComponent
class TestEntranceSingleShot(object):
    category = DEMO_CATEGORY
    editorTitle = 'Test Entrance Single Shot'
    domain = CGF.DomainOption.DomainClient
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger to subscribe', value=Triggers.AreaTriggerComponent)
    gunEffectsContoller = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Gun effects controller', value=Vehicular.GunEffectsController)


class EntranceSingleShotManager(CGF.ComponentManager):

    @onAddedQuery(TestEntranceSingleShot)
    def onEntranceAdded(self, entrance):
        trigger = entrance.trigger()
        if trigger:
            trigger.addEnterReaction(functools.partial(self.__onEnter, entrance))

    def __onEnter(self, entrance, who, where):
        gunEffectsContoller = entrance.gunEffectsContoller()
        if gunEffectsContoller:
            gunEffectsContoller.singleShot()


@registerComponent
class TestEntranceContinuousBurst(object):
    category = DEMO_CATEGORY
    editorTitle = 'Test Entrance Continuous Burst'
    domain = CGF.DomainOption.DomainClient
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger to subscribe', value=Triggers.AreaTriggerComponent)
    gunEffectsContoller = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Gun effects controller', value=Vehicular.GunEffectsController)


class EntranceContinuousBurstManager(CGF.ComponentManager):

    @onAddedQuery(TestEntranceContinuousBurst)
    def onEntranceAdded(self, entrance):
        trigger = entrance.trigger()
        if trigger:
            trigger.addEnterReaction(functools.partial(self.__onEnter, entrance))
            trigger.addExitReaction(functools.partial(self.__onExit, entrance))

    def __onEnter(self, entrance, who, where):
        controller = entrance.gunEffectsContoller()
        if controller:
            controller.startContinuousBurst()

    def __onExit(self, entrance, who, where):
        controller = entrance.gunEffectsContoller()
        if controller:
            controller.stopContinuousBurst()
