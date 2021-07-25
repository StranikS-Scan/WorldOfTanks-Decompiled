# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/test_triggers.py
import functools
import CGF
import GameplayDebug
import GenericComponents
import Triggers
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery

class TestEntranceNotifier(CGFComponent):
    category = DEMO_CATEGORY
    textComponent = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Text component to output', value=GameplayDebug.DebugTextComponent)
    trigger = ComponentProperty(type=CGFMetaTypes.LINK, editorName='AreaTrigger to subscribe', value=Triggers.AreaTriggerComponent)
    title = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Title', value='Area')

    def __init__(self):
        super(TestEntranceNotifier, self).__init__()
        self.__log = ''
        self.__messageCount = 0

    def addMessage(self, message):
        if self.__messageCount >= 10:
            self.__log = ''
            self.__messageCount = 0
        self.__messageCount += 1
        self.__log += message
        self.__flushText()

    def __flushText(self):
        text = self.textComponent()
        if text:
            text.setText(self.__log, (0, 0, 0), (1.0, 1.0, 1.0, 1.0))


class EntranceModifierManager(CGF.ComponentManager):

    @onAddedQuery(TestEntranceNotifier)
    def onEntranceAdded(self, entrance):
        trigger = entrance.trigger()
        if trigger:
            trigger.addEnterReaction(functools.partial(self.__onEnter, entrance))
            trigger.addExitReaction(functools.partial(self.__onExit, entrance))

    def __onEnter(self, entrance, who, where):
        transform = who.findComponentByType(GenericComponents.TransformComponent)
        entrance.addMessage('\n{0} was entered at {1}'.format(entrance.title, transform.worldPosition))

    def __onExit(self, entrance, who, where):
        transform = who.findComponentByType(GenericComponents.TransformComponent)
        entrance.addMessage('\n{0} was exited at {1}'.format(entrance.title, transform.worldPosition))
