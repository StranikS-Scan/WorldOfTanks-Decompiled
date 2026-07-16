# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/test_triggers.py
from __future__ import absolute_import
import functools
import CGF
import GameplayDebug
import GenericComponents
import Triggers
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.registration import ComponentProperty, registerComponent
from HealthComponent import HealthComponent

@registerComponent
class ShowHealthInfoComponent(object):
    group = DEMO_CATEGORY
    editorTitle = 'Show Health Info Component'
    domain = CGF.Domain.ClientEditor


@registerComponent
class TestEntranceNotifier(object):
    group = DEMO_CATEGORY
    editorTitle = 'Test Entrance Notifier'
    domain = CGF.Domain.Client
    textComponent = ComponentProperty(type=CGF.PropertyType.Link, editorName='Text component to output', value=GameplayDebug.DebugTextComponent)
    trigger = ComponentProperty(type=CGF.PropertyType.Link, editorName='AreaTrigger to subscribe', value=Triggers.AreaTriggerComponent)
    title = ComponentProperty(type=CGF.PropertyType.String, editorName='Title', value='Area')

    def __init__(self):
        super(TestEntranceNotifier, self).__init__()
        self.__log = ''
        self.__messageCount = 0

    def addMessage(self, message, text):
        if self.__messageCount >= 10:
            self.__log = ''
            self.__messageCount = 0
        self.__messageCount += 1
        self.__log += message
        self.__flushText(text)

    def __flushText(self, text):
        if text:
            text.setText(self.__log, (0, 0, 0), (1.0, 1.0, 1.0, 1.0))


class EntranceModifierSystem(CGF.System):
    EntranceActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(TestEntranceNotifier))
    AreaTriggerAccess = CGF.AccessReaction(CGF.Rw(Triggers.AreaTriggerComponent))
    DebugTextAccess = CGF.AccessReaction(CGF.Rw(GameplayDebug.DebugTextComponent))
    EntranceAccess = CGF.AccessReaction(CGF.Rw(TestEntranceNotifier))
    TransformAccess = CGF.AccessReaction(CGF.Rw(CGF.TransformComponent))
    Reactions = CGF.Reactions(EntranceActivated, AreaTriggerAccess, DebugTextAccess, EntranceAccess, TransformAccess)

    def update(self):
        triggerAccess = self.reaction(self.AreaTriggerAccess)
        for go, entrance in self.reaction(self.EntranceActivated):
            self._onEntranceAdded(go, entrance, triggerAccess)

    def _onEntranceAdded(self, entranceObj, entrance, triggerAccess):
        trigger = triggerAccess.find(entrance.trigger)
        if trigger:
            trigger.addEnterReaction(functools.partial(self.__onEnter, entranceObj))
            trigger.addExitReaction(functools.partial(self.__onExit, entranceObj))

    def __onEnter(self, entranceObj, who, where):
        transformAccess = self.reaction(self.TransformAccess)
        entranceAccess = self.reaction(self.EntranceAccess)
        textAccess = self.reaction(self.DebugTextAccess)
        transform = transformAccess.find(who)
        entrance = entranceAccess.find(entranceObj)
        text = textAccess.find(entrance.textComponent)
        entrance.addMessage('\n{0} was entered at {1}'.format(entrance.title, transform.worldPosition), text)

    def __onExit(self, entranceObj, who, where):
        transformAccess = self.reaction(self.TransformAccess)
        entranceAccess = self.reaction(self.EntranceAccess)
        textAccess = self.reaction(self.DebugTextAccess)
        transform = transformAccess.find(who)
        entrance = entranceAccess.find(entranceObj)
        text = textAccess.find(entrance.textComponent)
        entrance.addMessage('\n{0} was exited at {1}'.format(entrance.title, transform.worldPosition), text)


class TestHealthMonitoringSystem(CGF.System):
    HealthInfoActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(ShowHealthInfoComponent), CGF.No(GameplayDebug.DebugTextComponent))
    HealthIterate = CGF.IterateReaction(CGF.ActiveOnly, ShowHealthInfoComponent, CGF.Ro(HealthComponent), CGF.Rw(GameplayDebug.DebugTextComponent))
    GradationIterate = CGF.IterateReaction(CGF.ActiveOnly, ShowHealthInfoComponent, CGF.Ro(GenericComponents.HealthGradationComponent), CGF.Ro(HealthComponent), CGF.Rw(GameplayDebug.DebugTextComponent))
    Reactions = CGF.Reactions(HealthInfoActivated, HealthIterate, GradationIterate)

    def update(self):
        for go, _ in self.reaction(self.HealthInfoActivated):
            self._onAddedShowHealthInfo(go)

        for _, health, debugText in self.reaction(self.HealthIterate):
            self._showCurrentHealth(health, debugText)

        for _, gradation, health, debugText in self.reaction(self.GradationIterate):
            self._showExplosion(gradation, health, debugText)

    def _onAddedShowHealthInfo(self, go):
        q = CGF.CommandQueue(self.gom)
        q.createComponent(go, GameplayDebug.DebugTextComponent, '', (0, 0, 0), (1.0, 1.0, 1.0, 1.0))

    def _showCurrentHealth(self, health, debugText):
        debugText.addFrameText('Current health: %d, max health: %d' % (health.health, health.maxHealth))

    def _showExplosion(self, gradation, health, debugText):
        gradations = {GenericComponents.EHealthGradation.RED_ZONE: 'Red',
         GenericComponents.EHealthGradation.YELLOW_ZONE: 'Yellow',
         GenericComponents.EHealthGradation.GREEN_ZONE: 'Green'}
        zone = gradation.getHealthZone(health.health, health.maxHealth)
        debugText.addFrameText('Gradation: {0}'.format(gradations[zone]))
