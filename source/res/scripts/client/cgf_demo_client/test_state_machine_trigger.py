# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/test_state_machine_trigger.py
import logging
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes
import CGF
import GenericComponents
import Triggers
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
_logger = logging.getLogger(__name__)

class TestStateMachineStatesActivator(CGFComponent):
    category = DEMO_CATEGORY
    statesList = ComponentProperty(type=CGFMetaTypes.STRING_LIST, editorName='States', value=('Click', 'BowlClick'))
    animator = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Animator', value=GenericComponents.AnimatorComponent)
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Time trigger', value=Triggers.TimeTriggerComponent)

    def __init__(self):
        super(TestStateMachineStatesActivator, self).__init__()
        self.__index = 0
        self.__callbackID = None
        return

    def switchState(self):
        statesSize = len(self.statesList)
        if statesSize == 0:
            return
        else:
            if self.animator is not None:
                if self.__index >= len(self.statesList):
                    self.__index = 0
                _logger.debug('TestStateMachineStatesActivator. Set State %s', self.statesList[self.__index])
                self.animator().setTrigger(self.statesList[self.__index])
                self.__index += 1
            return


class StateMachineActivatorManager(CGF.ComponentManager):

    @onAddedQuery(TestStateMachineStatesActivator)
    def onActivatorAdded(self, activator):
        if activator.trigger is not None:
            activator.callbackID = activator.trigger().addFireReaction(lambda x: activator.switchState())
        return

    @onRemovedQuery(TestStateMachineStatesActivator)
    def onActivatorRemoved(self, activator):
        if activator.trigger is not None and activator.callbackID is not None:
            activator.trigger().removeFireReaction(activator.callbackID)
        return
