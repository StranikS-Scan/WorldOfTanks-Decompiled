# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/arena_component_system/step_repair_point_component.py
from client_arena_component_system import ClientArenaComponent
import Event

class StepRepairPointComponent(ClientArenaComponent):
    stepRepairPoints = property(lambda self: self.__stepRepairPoints)
    repairPointPlayerActions = property(lambda self: self.__repairPointPlayerAction)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__stepRepairPoints = []
        self.__repairPointPlayerAction = {}
        self.onStepRepairPointAdded = Event.Event(self._eventManager)
        self.onStepRepairPointActiveStateChanged = Event.Event(self._eventManager)
        self.onStepRepairPointPlayerAction = Event.Event(self._eventManager)

    def destroy(self):
        ClientArenaComponent.destroy(self)
        self.__stepRepairPoints = []
        self.__repairPointPlayerAction.clear()

    def addStepRepairPoint(self, stepRepairPoint):
        self.__stepRepairPoints.append(stepRepairPoint)
        self.onStepRepairPointAdded(stepRepairPoint)

    def removeStepRepairPoint(self, stepRepairPoint):
        if stepRepairPoint.id in self.__repairPointPlayerAction:
            self.__repairPointPlayerAction.pop(stepRepairPoint.id)
        self.__stepRepairPoints.remove(stepRepairPoint)

    def stepRepairPointActiveStateChanged(self, stepRepairPoint):
        self.onStepRepairPointActiveStateChanged(stepRepairPoint.id, stepRepairPoint.isActiveForPlayerTeam())

    def stepRepairPointPlayerAction(self, repairPointIndex, action, nextActionTime, pointsHealed):
        self.__repairPointPlayerAction[repairPointIndex] = (action, nextActionTime, pointsHealed)
        self.onStepRepairPointPlayerAction(repairPointIndex, action, nextActionTime, pointsHealed)

    def getRepairPointPlayerAction(self, repairPointIndex):
        return self.__repairPointPlayerAction[repairPointIndex] if repairPointIndex in self.__repairPointPlayerAction else None

    def getClosestRepairPoint(self, pos):
        chosenRepairPoint = None
        distBuffer = 20000000000.0
        for srp in self.stepRepairPoints:
            if not srp.isActiveForPlayerTeam():
                continue
            dist = srp.position.distTo(pos)
            if dist < distBuffer:
                chosenRepairPoint = srp
                distBuffer = dist

        return chosenRepairPoint
