# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/commands/commands_queue.py
import typing
from RTSShared import MAX_ORDERS_QUEUE_SIZE, RTSCommandQueuePosition
from gui.battle_control.controllers.commander import markers
from gui.battle_control.controllers.commander.commands import makeCommand
from helpers.CallbackDelayer import CallbackDelayer
from helpers import weakProxy, dependency
from skeletons.helpers.statistics import IStatisticsCollector
if typing.TYPE_CHECKING:
    import Math
    from gui.battle_control.controllers.commander.interfaces import IProxyVehicle, ICommand
    from RTSShared import RTSEvent

class CommandsQueue(CallbackDelayer):
    __slots__ = ('__vehicle', '__commands', '__markers', '__lastPosition', '__isPositionsUpdated')
    statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self, owner):
        super(CommandsQueue, self).__init__()
        self.__vehicle = weakProxy(owner)
        self.__commands = []
        self.__markers = []
        self.__lastPosition = None
        self.__isPositionsDirty = False
        return

    @property
    def activeCommand(self):
        return self.__commands[0] if self.__commands else None

    @property
    def lastCommandInQueue(self):
        return self.__commands[-1] if self.__commands else None

    @property
    def targetPosition(self):
        activeCommand = self.activeCommand
        return activeCommand.position if activeCommand is not None else None

    @property
    def lastPosition(self):
        return self.__lastPosition

    @property
    def getNumCommandsInQueue(self):
        numCommandsInQueue = len(self.__commands)
        return numCommandsInQueue

    def update(self):
        for command in self.__commands[:]:
            command.update()
            if command.isCompleted:
                self.__remove(command)
                self.__isPositionsDirty = True

        activeCommand = self.activeCommand
        if activeCommand is not None and not activeCommand.isExecuted:
            activeCommand.execute()
            self.__isPositionsDirty = True
        if self.__isPositionsDirty:
            self.__isPositionsDirty = False
            self.__updatePositions()
        return

    def canQueueCommand(self, commandTypeName, executeNow):
        if not self.__vehicle.isEnabled:
            return False
        else:
            if not executeNow:
                if len(self.__commands) > MAX_ORDERS_QUEUE_SIZE:
                    return False
                lastCommand = self.lastCommandInQueue
                if lastCommand is not None and not lastCommand.canQueueCommand(commandTypeName):
                    return False
            return True

    def shouldReplaceLastQueued(self, commandTypeName):
        lastCommand = self.lastCommandInQueue
        return lastCommand.canReplaceQueuedCommand(commandTypeName) if lastCommand is not None else False

    def enqueue(self, commandTypeName, executeNow=False, **kwargs):
        if executeNow:
            self.clear()
        if not self.canQueueCommand(commandTypeName, executeNow):
            return False
        if not executeNow and self.shouldReplaceLastQueued(commandTypeName):
            self.__remove(self.lastCommandInQueue)
        command = makeCommand(commandTypeName, self.__vehicle, **kwargs)
        self.__commands.append(command)
        self.__isPositionsDirty = True
        queuePos = RTSCommandQueuePosition.SINGLE if len(self.__commands) == 1 else RTSCommandQueuePosition.LAST
        command.enqueued(queuePos)
        self.__vehicle.handleOnCommandEnqueued(command)
        self.statsCollector.apm.recordAction()
        return True

    def handleRTSEvent(self, event, position):
        if self.activeCommand is not None:
            self.activeCommand.handleRTSEvent(event, position)
        return

    def clear(self):
        map(self.__remove, self.__commands[:])
        self.__isPositionsDirty = True

    def onCommandUpdated(self):
        self.__isPositionsDirty = True

    def __updatePositions(self):
        while self.__markers:
            self.__markers.pop().fini()

        prevPosition = None
        lastCommandIndex = len(self.__commands) - 1
        for idx, command in enumerate(self.__commands):
            if lastCommandIndex == 0:
                queuePos = RTSCommandQueuePosition.SINGLE
            elif idx == lastCommandIndex:
                queuePos = RTSCommandQueuePosition.LAST
            elif idx == 0:
                queuePos = RTSCommandQueuePosition.CURRENT
            else:
                queuePos = RTSCommandQueuePosition.NEXT
            command.updateQueuePosition(queuePos)
            position = command.position
            if position is not None:
                if prevPosition is not None:
                    self.__markers.append(markers.PathMarker(prevPosition, position, queuePos))
                prevPosition = position

        self.__lastPosition = prevPosition
        return

    def __remove(self, command):
        self.__commands.remove(command)
        command.fini()
        self.__vehicle.handleOnCommandDequeued(command)
        self.__isPositionsUpdated = True
