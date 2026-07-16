# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/test_state_machine_trigger.py
from __future__ import absolute_import
import CGF
import GenericComponents
import Triggers
import logging
from cgf_script.registration import ComponentProperty, registerComponent
from cgf_demo.demo_category import DEMO_CATEGORY
_logger = logging.getLogger(__name__)

@registerComponent
class TestStateMachineStatesActivator(object):
    group = DEMO_CATEGORY
    editorTitle = 'Test State Machine States Activator'
    domain = CGF.Domain.ClientEditor
    statesList = ComponentProperty(type=CGF.PropertyType.StringList, editorName='States', value=('Click', 'BowlClick'))
    animator = ComponentProperty(type=CGF.PropertyType.Link, editorName='Animator', value=GenericComponents.AnimatorComponent)
    trigger = ComponentProperty(type=CGF.PropertyType.Link, editorName='Time trigger', value=Triggers.TimeTriggerComponent)

    def __init__(self):
        super(TestStateMachineStatesActivator, self).__init__()
        self.__index = 0
        self.callbackID = None
        return

    def switchState(self, animator):
        statesSize = len(self.statesList)
        if statesSize == 0:
            return
        if animator:
            if self.__index >= len(self.statesList):
                self.__index = 0
            _logger.debug('TestStateMachineStatesActivator. Set State %s', self.statesList[self.__index])
            animator.setTrigger(self.statesList[self.__index])
            self.__index += 1


class StateMachineActivatorSystem(CGF.System):
    ActivatorActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(TestStateMachineStatesActivator))
    ActivatorDeactivated = CGF.DeactivateReaction(CGF.ReactRo(TestStateMachineStatesActivator))
    AnimatorAccess = CGF.AccessReaction(CGF.Rw(GenericComponents.AnimatorComponent))
    ActivatorAccess = CGF.AccessReaction(CGF.Rw(TestStateMachineStatesActivator))
    TimeTriggerAccess = CGF.AccessReaction(CGF.Rw(Triggers.TimeTriggerComponent))
    Reactions = CGF.Reactions(ActivatorActivated, ActivatorDeactivated, AnimatorAccess, ActivatorAccess, TimeTriggerAccess)

    def update(self):
        triggerAccess = self.reaction(self.TimeTriggerAccess)
        for activator in self.reaction(self.ActivatorDeactivated):
            self._onActivatorRemoved(activator, triggerAccess)

        for go, activator in self.reaction(self.ActivatorActivated):
            self._onActivatorAdded(go, activator, triggerAccess)

    def _onActivatorAdded(self, activatorObj, activator, triggerAccess):
        if activator.trigger:
            trigger = triggerAccess.find(activator.trigger)
            if trigger:
                activator.callbackID = trigger.addFireReaction(lambda x: self.switchState(activatorObj))

    def _onActivatorRemoved(self, activator, triggerAccess):
        if activator.trigger and activator.callbackID is not None:
            trigger = triggerAccess.find(activator.trigger)
            if trigger:
                trigger.removeFireReaction(activator.callbackID)
        return

    def switchState(self, activatorObj):
        activatorAccess = self.reaction(self.ActivatorAccess)
        activator = activatorAccess.find(activatorObj)
        if activator.animator:
            animatorAccess = self.reaction(self.AnimatorAccess)
            animator = animatorAccess.find(activator.animator)
            activator.switchState(animator)
