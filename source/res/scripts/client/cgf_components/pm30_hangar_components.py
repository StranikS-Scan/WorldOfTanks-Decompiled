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
    from typing import Callable, Optional
PERSONAL_MISSIONS_SUB_HANGAR_IS_READY = 'pmSubHangarIsReady'
OPERATION = 'operation{}'
VEHICLE_FOR_OPERATION = 'vehicleForOperation{}'
STAGES_COMPONENT_FOR_OPERATION = 'stagesComponentForOperation{}'
OPERATION_IDS_RANGE = tuple(range(8, 12))
STAGES_RANGE = tuple(range(0, 16))

@registerComponent
class HangarOperationsComponent(object):
    editorTitle = 'Operations links'
    category = 'PersonalMissions 3.0'
    domain = CGF.Domain.ClientEditor
    operation8 = ComponentProperty(type=CGF.PropertyType.Link, editorName='operation 8', value=CGF.GameObject)
    operation9 = ComponentProperty(type=CGF.PropertyType.Link, editorName='operation 9', value=CGF.GameObject)
    operation10 = ComponentProperty(type=CGF.PropertyType.Link, editorName='operation 10', value=CGF.GameObject)
    operation11 = ComponentProperty(type=CGF.PropertyType.Link, editorName='operation 11', value=CGF.GameObject)

    def getOperationObject(self, operationID):
        return getattr(self, OPERATION.format(operationID))


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
        self.timers = {}

    def update(self):
        stagesAccess = self.reaction(self.StagesAccess)
        for _ in self.reaction(self.HangarOperationDeactivated):
            self.onHangarOperationRemoved(stagesAccess)

        for _, selection in self.reaction(self.MissionSelectionDeactivated):
            self.onSelectionRemoved(selection)

        for _, selection in self.reaction(self.MissionSelectionActivated):
            self.onSelectionAdded(selection)

        for hangarOperationsComponent in self.reaction(self.HangarOperationActivated):
            self.onHangarOperationAdded(hangarOperationsComponent, stagesAccess)

        self.tick()

    def onHangarOperationRemoved(self, stagesAccess):
        for operationID in OPERATION_IDS_RANGE:
            self.setVehicleGOForOperation(operationID, None)
            self.setStagesForOperation(stagesAccess, operationID, None)

        self.gameObjectsAreRemoved = True
        self.timers = {}
        self.onVehicleClick.clear()
        return

    def onHangarOperationAdded(self, hangarOperationsComponent, stagesAccess):
        self.gameObjectsAreRemoved = False
        for operationID in OPERATION_IDS_RANGE:
            self.setVehicleGOForOperation(operationID, hangarOperationsComponent.getOperationObject(operationID))
            vehicleForOperation = self.getVehicleForOperation(operationID)
            if vehicleForOperation and vehicleForOperation.valid:
                self.setStagesForOperation(stagesAccess, operationID, vehicleForOperation)

        g_eventBus.handleEvent(event_bus.SharedEvent(PERSONAL_MISSIONS_SUB_HANGAR_IS_READY), scope=EVENT_BUS_SCOPE.LOBBY)

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

    def setVehicleGOForOperation(self, operationID, vehicleGO):
        setattr(self, VEHICLE_FOR_OPERATION.format(operationID), self.gom.gameObject(vehicleGO) if vehicleGO else None)
        return

    def setStagesForOperation(self, stagesAccess, operationID, vehicleGO):
        setattr(self, STAGES_COMPONENT_FOR_OPERATION.format(operationID), stagesAccess.find(vehicleGO) if vehicleGO else None)
        return

    def getVehicleForOperation(self, operationID):
        return getattr(self, VEHICLE_FOR_OPERATION.format(operationID), None)

    def getStagesForOperation(self, operationID):
        return getattr(self, STAGES_COMPONENT_FOR_OPERATION.format(operationID), None)

    def onVehicleClickAction(self):
        self.onVehicleClick()
