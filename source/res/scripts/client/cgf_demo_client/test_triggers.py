# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/test_triggers.py
import functools
import CGF
import GameplayDebug
import GenericComponents
import Triggers
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onProcessQuery
from constants import IS_EDITOR
if IS_EDITOR:
    from cgf_components_common.state_components import HealthComponent
else:
    from HealthComponent import HealthComponent

@registerComponent
class ShowHealthInfoComponent(object):
    category = DEMO_CATEGORY
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor


@registerComponent
class TestEntranceNotifier(object):
    category = DEMO_CATEGORY
    domain = CGF.DomainOption.DomainClient
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


class TestHealthMonitoringManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, ShowHealthInfoComponent, CGF.No(GameplayDebug.DebugTextComponent))
    def onAddedShowHealthInfo(self, go, _):
        go.createComponent(GameplayDebug.DebugTextComponent, '', (0, 0, 0), (1.0, 1.0, 1.0, 1.0))

    @onProcessQuery(ShowHealthInfoComponent, HealthComponent, GameplayDebug.DebugTextComponent, tickGroup='Simulation')
    def showCurrentHealth(self, _, health, debugText):
        debugText.addFrameText('Current health: %d, max health: %d' % (health.health, health.maxHealth))

    @onProcessQuery(ShowHealthInfoComponent, GenericComponents.HealthGradationComponent, HealthComponent, GameplayDebug.DebugTextComponent, tickGroup='Simulation')
    def showExplosion(self, _, gradation, health, debugText):
        gradations = {GenericComponents.EHealthGradation.RED_ZONE: 'Red',
         GenericComponents.EHealthGradation.YELLOW_ZONE: 'Yellow',
         GenericComponents.EHealthGradation.GREEN_ZONE: 'Green'}
        zone = gradation.getHealthZone(health.health, health.maxHealth)
        debugText.addFrameText('Gradation: {0}'.format(gradations[zone]))
