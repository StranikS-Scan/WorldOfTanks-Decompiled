# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/pm30_hangar_components.py
import typing
import CGF
import Event
from cgf_components.hover_component import SelectionComponent
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerComponent
from cgf_script.managers_registrator import onAddedQuery, registerRule, Rule, registerManager, onRemovedQuery, tickGroup
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, event_bus
if typing.TYPE_CHECKING:
    from typing import Optional
PERSONAL_MISSIONS_3_SUB_HANGAR_IS_READY = 'pm3SubHangarIsReady'

@registerComponent
class HangarOperationsComponent(object):
    editorTitle = 'Operations links'
    category = 'PersonalMissions 3.0'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    operation8 = ComponentProperty(type=CGFMetaTypes.LINK, editorName='operation 8', value=CGF.GameObject)
    operation9 = ComponentProperty(type=CGFMetaTypes.LINK, editorName='operation 9', value=CGF.GameObject)
    operation10 = ComponentProperty(type=CGFMetaTypes.LINK, editorName='operation 10', value=CGF.GameObject)


@registerComponent
class PersonalMissionsSelectionComponent(object):
    editorTitle = 'PM Selection'
    category = 'PersonalMissions 3.0'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor


class HangarOperationsManager(CGF.ComponentManager):

    def __init__(self):
        super(HangarOperationsManager, self).__init__()
        self.onVehicleClick = Event.Event()
        self.gameObjectsAreRemoved = False
        self.vehicleForOperation8 = None
        self.vehicleForOperation9 = None
        self.vehicleForOperation10 = None
        self.stagesComponentForOperation8 = None
        self.stagesComponentForOperation9 = None
        self.stagesComponentForOperation10 = None
        self.timers = {}
        return

    @onRemovedQuery(CGF.GameObject, HangarOperationsComponent)
    def onHangarOperationRemoved(self, _, __):
        self.vehicleForOperation8 = None
        self.vehicleForOperation9 = None
        self.vehicleForOperation10 = None
        self.stagesComponentForOperation8 = None
        self.stagesComponentForOperation9 = None
        self.stagesComponentForOperation10 = None
        self.gameObjectsAreRemoved = True
        self.timers = {}
        self.onVehicleClick.clear()
        return

    @onAddedQuery(CGF.GameObject, HangarOperationsComponent)
    def onHangarOperationAdded(self, _, hangarOperationsComponent):
        self.gameObjectsAreRemoved = False
        self.vehicleForOperation8 = hangarOperationsComponent.operation8
        self.vehicleForOperation9 = hangarOperationsComponent.operation9
        self.vehicleForOperation10 = hangarOperationsComponent.operation10
        if self.vehicleForOperation8 and self.vehicleForOperation8.isValid():
            self.stagesComponentForOperation8 = self.vehicleForOperation8.findComponentByType(AssemblingStagesComponent)
        if self.vehicleForOperation9 and self.vehicleForOperation9.isValid():
            self.stagesComponentForOperation9 = self.vehicleForOperation9.findComponentByType(AssemblingStagesComponent)
        if self.vehicleForOperation10 and self.vehicleForOperation10.isValid():
            self.stagesComponentForOperation10 = self.vehicleForOperation10.findComponentByType(AssemblingStagesComponent)
        g_eventBus.handleEvent(event_bus.SharedEvent(PERSONAL_MISSIONS_3_SUB_HANGAR_IS_READY), scope=EVENT_BUS_SCOPE.LOBBY)

    @onAddedQuery(PersonalMissionsSelectionComponent, SelectionComponent)
    def onSelectionAdded(self, _, selectionComponent):
        selectionComponent.onClickAction += self.onVehicleClickAction

    @onRemovedQuery(PersonalMissionsSelectionComponent, SelectionComponent)
    def onSelectionRemoved(self, _, selectionComponent):
        selectionComponent.onClickAction -= self.onVehicleClickAction

    @tickGroup(groupName='Simulation')
    def tick(self):
        for key in list(self.timers):
            if self.timers[key]['duration'] > 0:
                self.timers[key]['duration'] -= self.clock.gameDelta
                if self.timers[key]['duration'] <= 0:
                    callback = self.timers.pop(key)['callback']
                    callback()

    def addTimer(self, timerName, duration, callback):
        self.timers.update({timerName: {'duration': duration,
                     'callback': callback}})

    def onVehicleClickAction(self):
        self.onVehicleClick()


@registerRule
class HangarOperationsRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor

    @registerManager(HangarOperationsManager)
    def reg1(self):
        return None


def getComponentProperties(stageKey):
    return {stageKey.format(i):ComponentProperty(type=CGFMetaTypes.LINK, editorName=stageKey.format(i), value=CGF.GameObject) for i in range(0, 16)}


Fades = type('Fades', (object,), getComponentProperties('stage_{}_fade'))
Stages = type('Stages', (Fades,), getComponentProperties('stage_{}'))

@registerComponent
class AssemblingStagesComponent(Stages):
    editorTitle = 'Assembling Stages'
    category = 'PersonalMissions 3.0'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    cape = ComponentProperty(type=CGFMetaTypes.LINK, editorName='cape', value=CGF.GameObject)
    support = ComponentProperty(type=CGFMetaTypes.LINK, editorName='support', value=CGF.GameObject)
