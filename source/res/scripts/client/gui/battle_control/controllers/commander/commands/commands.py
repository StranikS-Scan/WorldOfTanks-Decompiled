# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/commands/commands.py
import typing
import BigWorld
from RTSShared import RTSOrder, RTSEvent, RTSQuery, RTSQueryResultCode, COMMAND_NAME, RTSCommandResult
from gui.battle_control.controllers.commander import markers
from gui.battle_control.controllers.commander.interfaces import ICommand
from helpers import dependency, weakProxy
from vehicle_formation import getHeading
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Any, Dict
    from RTSShared import RTSQueryResult
    from gui.battle_control.controllers.commander.proxies.vehicle import _ControllableProxyVehicle
    from gui.battle_control.controllers.commander.interfaces import ICommandsGroup, IProxyVehicle

class _Command(ICommand):
    __slots__ = ('_order', '_isExecuted', '_commandResult', '_companions', '__entity', '__groupID')
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, entity=None, order=None, companions=None, groupID=None, **kwargs):
        super(_Command, self).__init__()
        self.__entity = weakProxy(entity)
        self.__groupID = groupID
        self._companions = companions
        self._order = order
        self._isExecuted = False
        self._commandResult = RTSCommandResult.NONE

    @property
    def isExecuted(self):
        return self._isExecuted

    @property
    def isCompleted(self):
        return self._commandResult != RTSCommandResult.NONE

    @property
    def result(self):
        return self._commandResult

    @property
    def position(self):
        return None

    @property
    def heading(self):
        return None

    @property
    def order(self):
        return self._order

    @property
    def groupID(self):
        return self.__groupID

    @property
    def group(self):
        return self.entity.getCommandsGroup(self.groupID)

    @property
    def entity(self):
        return self.__entity

    @property
    def companions(self):
        return self._companions

    def enqueued(self, queuePos):
        pass

    def execute(self):
        if not self.__entity.isAlive:
            self._finishCommand(RTSCommandResult.ABORTED)
            return
        self._isExecuted = True
        self._execute()

    def fini(self):
        if not self.isCompleted:
            self._finishCommand(RTSCommandResult.ABORTED)
        self.entity.path.setIsAutonomousMove(True)

    def updateQueuePosition(self, queuePos):
        pass

    def canQueueCommand(self, commandTypeName):
        return True

    def canReplaceQueuedCommand(self, commandTypeName):
        return False

    def handleRTSEvent(self, event, position):
        pass

    def _execute(self):
        pass

    def update(self):
        if not self._isExecuted:
            return False
        if not self.__entity.isAlive:
            self._finishCommand(RTSCommandResult.ABORTED)

    def _finishCommand(self, result):
        if self._commandResult == RTSCommandResult.NONE:
            self._commandResult = result
            if self.isExecuted:
                self.entity.onCommandComplete(self)


class AttackCommand(_Command):
    __slots__ = ('_target', '_attackMarker')

    def __init__(self, target=None, force=False, **kwargs):
        order = RTSOrder.FORCE_ATTACK_ENEMY if force else RTSOrder.ATTACK_ENEMY
        super(AttackCommand, self).__init__(order=order, **kwargs)
        self._target = weakProxy(target)
        self._attackMarker = None
        return

    def enqueued(self, queuePos):
        self._attackMarker = markers.AttackMarker(self.entity, self._target, queuePos)
        self._target.markAsTarget(self, self.order)

    def updateQueuePosition(self, queuePos):
        if self._attackMarker is not None:
            self._attackMarker.setCommandQueuePosition(queuePos)
        return

    def canQueueCommand(self, commandTypeName):
        return COMMAND_NAME.ATTACK == commandTypeName

    def canReplaceQueuedCommand(self, commandTypeName):
        return COMMAND_NAME.ATTACK == commandTypeName

    def handleRTSEvent(self, event, position):
        if event == RTSEvent.ON_TARGET_LOST:
            self._finishCommand(RTSCommandResult.FAILED)

    def fini(self):
        self._target.unmarkAsTarget(self)
        if self._attackMarker is not None:
            self._attackMarker.fini()
        self._attackMarker = None
        super(AttackCommand, self).fini()
        return

    def update(self):
        super(AttackCommand, self).update()
        if not self.isCompleted:
            if self._target.isAlive:
                self._attackMarker.update()
            else:
                self._finishCommand(RTSCommandResult.SUCCESS)

    def _execute(self):
        self.entity.path.setIsAutonomousMove(True)
        self.entity.updateRTSOrder(order=self.order, target=self._target.id, companions=self.companions)


class MoveCommand(_Command):
    __slots__ = ('__position', '__heading', '__target', '_order', '__baseID', '__baseTeam', '__marker', '__queuePos', '__navMeshQueryID', '__vehicleModel')

    def __init__(self, position=None, heading=None, target=None, isAggressive=False, isRetreat=False, controlPoint=None, marker=None, vehicleModel=None, **kwargs):
        self.__position = position
        self.__heading = heading
        self.__target = target
        self.__marker = marker
        self.__baseID = None
        self.__baseTeam = None
        self.__queuePos = None
        self.__navMeshQueryID = None
        self.__vehicleModel = vehicleModel
        if isRetreat:
            order = RTSOrder.RETREAT
        elif controlPoint is None:
            order = RTSOrder.FORCE_GO_TO_POSITION if isAggressive else RTSOrder.GO_TO_POSITION
        else:
            self.__baseID, self.__baseTeam = controlPoint
            arenaDP = self._sessionProvider.getArenaDP()
            order = RTSOrder.DEFEND_THE_BASE if arenaDP.isAllyTeam(self.__baseTeam) else RTSOrder.CAPTURE_THE_BASE
        super(MoveCommand, self).__init__(order=order, **kwargs)
        return

    @property
    def position(self):
        return self.__position

    @property
    def heading(self):
        return self.__heading

    @property
    def controlPoint(self):
        return (self.__baseID, self.__baseTeam)

    def handleRTSEvent(self, event, position):
        if event == RTSEvent.ON_TARGET_REACHED:
            self._finishCommand(RTSCommandResult.SUCCESS)
        elif event == RTSEvent.ON_ORDER_MODIFIED_BY_SERVER and position is not None:
            self._correctPosition(position)
        elif event == RTSEvent.ON_ORDER_CANCELED_BY_SERVER:
            self._movementFailed()
        return

    def enqueued(self, queuePos):
        marker = self._getOrCreateMarker()
        marker.orderType = self.order
        marker.setVisible(True)
        context = {'position': self.position,
         'companions': self.companions}
        self.__navMeshQueryID = self.entity.queryRTSData(RTSQuery.POSITION_ON_NAV_MESH, context, self._onNavPosReceived)

    def canQueueCommand(self, commandTypeName):
        return False if self._order in (RTSOrder.DEFEND_THE_BASE, RTSOrder.CAPTURE_THE_BASE) else super(MoveCommand, self).canQueueCommand(commandTypeName)

    def updateQueuePosition(self, queuePos):
        self._getOrCreateMarker().setCommandQueuePosition(queuePos)

    def onPreviewAppeared(self):
        if self.__marker is not None:
            self.__marker.cleanVehicleMarkerRef()
        return

    def fini(self):
        if self.__marker is not None:
            self.__marker.fini()
            self.__marker = None
        self.__navMeshQueryID = None
        super(MoveCommand, self).fini()
        return

    def _getOrCreateMarker(self):
        if self.__marker is None:
            self.__marker = markers.TerrainOrderMarker(self.entity.id, self.order, self.__position, self.__heading, self.__vehicleModel)
        return self.__marker

    def _execute(self):
        isCaptureTheBase = self.order == RTSOrder.DEFEND_THE_BASE or self.order == RTSOrder.CAPTURE_THE_BASE
        if isCaptureTheBase and self.__baseID != 1:
            self.__baseID = 1
        self.entity.path.setIsAutonomousMove(False)
        self.entity.updateRTSOrder(order=self.order, position=self.__position, heading=self.__heading, baseID=self.__baseID, baseTeam=self.__baseTeam, target=self.__target, companions=self.companions)

    def _updatePosition(self, newPosition):
        if self.__position != newPosition:
            self._getOrCreateMarker().move(newPosition)
            self.__position = newPosition
            self.entity.onCommandUpdated()

    def _correctPosition(self, newPosition):
        if self.__position != newPosition:
            markers.InvalidPositionMarker(self.__position)
            self._updatePosition(newPosition)

    def _movementFailed(self):
        markers.InvalidPositionMarker(self.__position)
        self._finishCommand(RTSCommandResult.FAILED)

    def _onNavPosReceived(self, queryResult):
        if queryResult.queryID == self.__navMeshQueryID:
            self.__navMeshQueryID = None
            resultCode = queryResult.resultCode
            if resultCode == RTSQueryResultCode.MODIFIED:
                self._correctPosition(queryResult.position)
            elif resultCode == RTSQueryResultCode.FAILED:
                self._movementFailed()
            elif resultCode == RTSQueryResultCode.OK:
                self._updatePosition(queryResult.position)
        return


class PursuitTargetCommand(_Command):
    __slots__ = ('__position', '__heading', '__marker')

    def __init__(self, order=None, position=None, **kwargs):
        super(PursuitTargetCommand, self).__init__(order=order, **kwargs)
        self.__position = position
        direction = self.entity.position - position
        self.__heading = getHeading(direction, False)
        self.__marker = None
        return

    def fini(self):
        if self.__marker is not None:
            self.__marker.fini()
            self.__marker = None
        super(PursuitTargetCommand, self).fini()
        return

    def handleRTSEvent(self, event, _):
        if event in (RTSEvent.ON_TARGET_DETECTED, RTSEvent.ON_TARGET_REACHED, RTSEvent.ON_TARGET_LOST):
            self._finishCommand(RTSCommandResult.SUCCESS)

    def _execute(self):
        self.entity.path.setIsAutonomousMove(True)
        self.__marker = markers.TerrainOrderMarker(self.entity.id, self.order, self.__position, self.__heading, BigWorld.Model(''))


_COMMAND_CLS_MAP = {COMMAND_NAME.ATTACK: AttackCommand,
 COMMAND_NAME.MOVE: MoveCommand,
 COMMAND_NAME.PURSUIT: PursuitTargetCommand}

def makeCommand(commandTypeName, entity, **kwargs):
    return _COMMAND_CLS_MAP[commandTypeName](entity=entity, **kwargs)
