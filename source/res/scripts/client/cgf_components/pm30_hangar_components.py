# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/pm30_hangar_components.py
from __future__ import absolute_import
import typing
import CGF
import Event
from cgf_components.hover_component import SelectionComponent
from cgf_script.registration import ComponentProperty, registerComponent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, event_bus
if typing.TYPE_CHECKING:
    from typing import Optional
PERSONAL_MISSIONS_3_SUB_HANGAR_IS_READY = 'pm3SubHangarIsReady'

@registerComponent
class HangarOperationsComponent(object):
    editorTitle = 'Operations links'
    category = 'PersonalMissions 3.0'
    domain = CGF.Domain.ClientEditor
    operation8 = ComponentProperty(type=CGF.PropertyType.Link, editorName='operation 8', value=CGF.GameObject)
    operation9 = ComponentProperty(type=CGF.PropertyType.Link, editorName='operation 9', value=CGF.GameObject)
    operation10 = ComponentProperty(type=CGF.PropertyType.Link, editorName='operation 10', value=CGF.GameObject)


@registerComponent
class PersonalMissionsSelectionComponent(object):
    editorTitle = 'PM Selection'
    category = 'PersonalMissions 3.0'
    domain = CGF.Domain.ClientEditor


def getComponentProperties(stageKey):
    return {stageKey.format(i):ComponentProperty(type=CGF.PropertyType.Link, editorName=stageKey.format(i), value=CGF.GameObject) for i in range(0, 16)}


Fades = type('Fades', (object,), getComponentProperties('stage_{}_fade'))
Stages = type('Stages', (Fades,), getComponentProperties('stage_{}'))

@registerComponent
class AssemblingStagesComponent(Stages):
    editorTitle = 'Assembling Stages'
    category = 'PersonalMissions 3.0'
    domain = CGF.Domain.ClientEditor
    cape = ComponentProperty(type=CGF.PropertyType.Link, editorName='cape', value=CGF.GameObject)
    support = ComponentProperty(type=CGF.PropertyType.Link, editorName='support', value=CGF.GameObject)


class HangarOperationsSystem(CGF.System):
    HangarOperationActivated = CGF.ActivateReaction(CGF.ReactRo(HangarOperationsComponent))
    HangarOperationDeactivated = CGF.DeactivateReaction(CGF.ReactRo(HangarOperationsComponent))
    HangarOperationIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(HangarOperationsComponent))
    MissionSelectionActivated = CGF.ActivateReaction(CGF.ReactRo(PersonalMissionsSelectionComponent), CGF.Rw(SelectionComponent))
    MissionSelectionDeactivated = CGF.DeactivateReaction(CGF.ReactRw(PersonalMissionsSelectionComponent), CGF.Rw(SelectionComponent))
    StagesAccess = CGF.AccessReaction(CGF.Ro(AssemblingStagesComponent))
    Reactions = CGF.Reactions(HangarOperationActivated, HangarOperationDeactivated, HangarOperationIterate, MissionSelectionActivated, MissionSelectionDeactivated, StagesAccess)

    def __init__(self):
        super(HangarOperationsSystem, self).__init__()
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

    def update(self):
        for _ in self.reaction(self.HangarOperationDeactivated):
            self.onHangarOperationRemoved()

        for _, selection in self.reaction(self.MissionSelectionDeactivated):
            self.onSelectionRemoved(selection)

        for _, selection in self.reaction(self.MissionSelectionActivated):
            self.onSelectionAdded(selection)

        stagesAccess = self.reaction(self.StagesAccess)
        for hangarOperationsComponent in self.reaction(self.HangarOperationActivated):
            self.onHangarOperationAdded(hangarOperationsComponent, stagesAccess)

        self.tick()

    def onHangarOperationRemoved(self):
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

    def onHangarOperationAdded(self, hangarOperationsComponent, stagesAccess):
        self.gameObjectsAreRemoved = False
        goManager = self.gom
        self.vehicleForOperation8 = goManager.gameObject(hangarOperationsComponent.operation8)
        self.vehicleForOperation9 = goManager.gameObject(hangarOperationsComponent.operation9)
        self.vehicleForOperation10 = goManager.gameObject(hangarOperationsComponent.operation10)
        if self.vehicleForOperation8 and self.vehicleForOperation8.valid:
            self.stagesComponentForOperation8 = stagesAccess.find(self.vehicleForOperation8)
        if self.vehicleForOperation9 and self.vehicleForOperation9.valid:
            self.stagesComponentForOperation9 = stagesAccess.find(self.vehicleForOperation9)
        if self.vehicleForOperation10 and self.vehicleForOperation10.valid:
            self.stagesComponentForOperation10 = stagesAccess.find(self.vehicleForOperation10)
        g_eventBus.handleEvent(event_bus.SharedEvent(PERSONAL_MISSIONS_3_SUB_HANGAR_IS_READY), scope=EVENT_BUS_SCOPE.LOBBY)

    def onSelectionAdded(self, selectionComponent):
        selectionComponent.onClickAction += self.onVehicleClickAction

    def onSelectionRemoved(self, selectionComponent):
        selectionComponent.onClickAction -= self.onVehicleClickAction

    def tick(self):
        for key in list(self.timers):
            if self.timers[key]['duration'] > 0:
                self.timers[key]['duration'] -= self.clock.updateDelta
                if self.timers[key]['duration'] <= 0:
                    callback = self.timers.pop(key)['callback']
                    callback()

    def addTimer(self, timerName, duration, callback):
        self.timers.update({timerName: {'duration': duration,
                     'callback': callback}})

    def onVehicleClickAction(self):
        self.onVehicleClick()
