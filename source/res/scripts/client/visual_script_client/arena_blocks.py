# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/arena_blocks.py
import weakref
from typing import List
import BigWorld
import Math
from ArenaType import g_cache
from constants import IS_VS_EDITOR, ARENA_PERIOD, ARENA_PERIOD_NAMES, CollisionFlags, TEAMS_IN_ARENA
from visual_script.block import Block, InitParam
from visual_script.dependency import dependencyImporter
from visual_script.misc import ASPECT, errorVScript
from visual_script.slot_types import SLOT_TYPE, arrayOf
from visual_script.arena_blocks import ArenaMeta, GetUDOByNameBase, GetDataFromStorageBase
from visual_script.tunable_event_block import TunableEventBlock
from PlayerEvents import g_playerEvents
helpers, clientArena, dependency, battle_session = dependencyImporter('helpers', 'ClientArena', 'helpers.dependency', 'skeletons.gui.battle_session')

class ClientArena(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(ClientArena, self).__init__(*args, **kwargs)
        self._arena = self._makeDataOutputSlot('arena', SLOT_TYPE.ARENA, self._execArena)

    def _execArena(self):
        arena = getattr(BigWorld.player(), 'arena')
        self._arena.setValue(weakref.proxy(arena) if arena is not None else None)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class GetControlPoint(Block, ArenaMeta):

    class TeamBase(object):

        def __init__(self, team, baseID):
            self.team = team
            self.baseID = baseID

    _CACHE = {}

    def __init__(self, *args, **kwargs):
        super(GetControlPoint, self).__init__(*args, **kwargs)
        self._team = self._makeDataInputSlot('teamId', SLOT_TYPE.INT)
        self._baseID = self._makeDataInputSlot('baseId', SLOT_TYPE.INT)
        self._value = self._makeDataOutputSlot('value', SLOT_TYPE.CONTROL_POINT, self._execValue)

    def _execValue(self):
        baseKey = (self._team.getValue(), self._baseID.getValue())
        if baseKey not in GetControlPoint._CACHE:
            GetControlPoint._CACHE[baseKey] = GetControlPoint.TeamBase(*baseKey)
        self._value.setValue(weakref.proxy(GetControlPoint._CACHE[baseKey]))

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class GetActiveControlPoints(Block, ArenaMeta):
    TeamBase = GetControlPoint.TeamBase
    _CACHE = {}

    def __init__(self, *args, **kwargs):
        super(GetActiveControlPoints, self).__init__(*args, **kwargs)
        self._team = self._makeDataInputSlot('teamId', SLOT_TYPE.INT)
        self._value = self._makeDataOutputSlot('value', arrayOf(SLOT_TYPE.CONTROL_POINT), self._execValue)

    def _execValue(self):
        team = self._team.getValue()
        controlPoints = g_cache[BigWorld.player().arenaTypeID].controlPoints
        teamBasePositions = g_cache[BigWorld.player().arenaTypeID].teamBasePositions
        teambases = []
        if team == TEAMS_IN_ARENA.ANY_TEAM and controlPoints is not None:
            for i, _ in enumerate(controlPoints):
                baseKey = (team, i + 1)
                if baseKey not in self._CACHE:
                    self._CACHE[baseKey] = self.TeamBase(*baseKey)
                teambases.append(self._CACHE[baseKey])

        elif team != TEAMS_IN_ARENA.ANY_TEAM and team <= len(teamBasePositions):
            for baseId in teamBasePositions[team - 1].iterkeys():
                baseKey = (team, baseId)
                if baseKey not in self._CACHE:
                    self._CACHE[baseKey] = self.TeamBase(*baseKey)
                teambases.append(self._CACHE[baseKey])

        self._value.setValue(map(weakref.proxy, teambases))
        return

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class OnCaptureControlPoint(TunableEventBlock, ArenaMeta):
    _EVENT_SLOT_NAMES = ['onStarted',
     'onStopped',
     'onUpdated',
     'onCompleted']

    def __init__(self, *args, **kwargs):
        super(OnCaptureControlPoint, self).__init__(*args, **kwargs)
        self._points = self._makeDataOutputSlot('points', SLOT_TYPE.INT, self._getPoints)
        self._invadersCount = self._makeDataOutputSlot('invadersCount', SLOT_TYPE.INT, self._getInvadersCount)
        self._controlPoint = self._makeDataInputSlot('controlPoint', SLOT_TYPE.CONTROL_POINT)

    @classmethod
    def blockIcon(cls):
        pass

    def onStartScript(self):
        arena = self.arena
        if arena is not None:
            arena.onTeamBasePointsUpdateAlt += self._capturingInfoUpdate
            arena.onTeamBaseCaptured += self._onCaptured
        return

    def onFinishScript(self):
        arena = self.arena
        if arena is not None:
            arena.onTeamBasePointsUpdateAlt -= self._capturingInfoUpdate
            arena.onTeamBaseCaptured -= self._onCaptured
        return

    @property
    def arena(self):
        return getattr(BigWorld.player(), 'arena') if not IS_VS_EDITOR else None

    def _isCurrControlPoint(self, baseID, team):
        controlPoint = self._controlPoint.getValue()
        return controlPoint is not None and controlPoint.baseID == baseID and controlPoint.team == team

    def _capturingInfoUpdate(self, team, baseID, lastData, currData):
        if not self._isCurrControlPoint(baseID, team) or self.arena is None:
            return
        else:
            lastPoints, lastInvadersCnt, _ = lastData
            points, invadersCnt, capturingStopped = currData
            if points != lastPoints:
                self._index = 2
                self._callUpdated()
            if capturingStopped or lastInvadersCnt > 0 and invadersCnt <= 0:
                self._index = 1
                self._callStopped()
            elif lastInvadersCnt <= 0 and invadersCnt > 0:
                self._index = 0
                self._callStarted()
            return

    def _onCaptured(self, team, baseID):
        if self._isCurrControlPoint(baseID, team):
            self._index = 3
            self._callCompleted()

    @TunableEventBlock.eventProcessor
    def _callUpdated(self):
        pass

    @TunableEventBlock.eventProcessor
    def _callStopped(self):
        pass

    @TunableEventBlock.eventProcessor
    def _callStarted(self):
        pass

    @TunableEventBlock.eventProcessor
    def _callCompleted(self):
        pass

    def _getPoints(self):
        controlPoint = self._controlPoint.getValue()
        if controlPoint is not None and self.arena is not None:
            self._points.setValue(self.arena.teamBasesData[controlPoint.team].get(controlPoint.baseID, clientArena.TeamBaseProvider(0, 0, False)).points)
        else:
            self._points.setValue(-1)
        return

    def _getInvadersCount(self):
        controlPoint = self._controlPoint.getValue()
        if controlPoint is not None and self.arena is not None:
            self._invadersCount.setValue(self.arena.teamBasesData[controlPoint.team].get(controlPoint.baseID, clientArena.TeamBaseProvider(0, 0, False)).invadersCnt)
        else:
            self._invadersCount.setValue(-1)
        return

    def validate(self):
        return 'ControlPoint value is required' if not self._controlPoint.hasValue() else super(OnCaptureControlPoint, self).validate()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class ArenaPeriod(Block, ArenaMeta):

    class PlayerArenaDummy(object):
        period = None

    def __init__(self, *args, **kwargs):
        super(ArenaPeriod, self).__init__(*args, **kwargs)
        self._isPeriodActive = self._makeDataOutputSlot('isActive', SLOT_TYPE.BOOL, self._execIsStart)
        self._timeFromStartSlot = self._makeDataOutputSlot('timeFromStart', SLOT_TYPE.FLOAT, self._execTimeFromStart)
        self._timeToEndSlot = self._makeDataOutputSlot('timeToEnd', SLOT_TYPE.FLOAT, self._execTimeToEnd)
        self._periodType = self._getInitParams()

    @property
    def _arena(self):
        return getattr(BigWorld.player(), 'arena', ArenaPeriod.PlayerArenaDummy)

    def _execIsStart(self):
        self._isPeriodActive.setValue(self._arena.period == self._periodType)

    def _execTimeFromStart(self):
        arena = self._arena
        if arena.period == self._periodType:
            time = max(0.0, BigWorld.serverTime() - (arena.periodEndTime - arena.periodLength))
            self._timeFromStartSlot.setValue(time)
        else:
            self._timeFromStartSlot.setValue(-1.0)

    def _execTimeToEnd(self):
        arena = self._arena
        if arena.period == self._periodType:
            timeToEnd = max(0.0, arena.periodEndTime - BigWorld.serverTime())
            self._timeToEndSlot.setValue(timeToEnd)
        else:
            self._timeToEndSlot.setValue(-1.0)

    @classmethod
    def blockIcon(cls):
        pass

    def captionText(self):
        return 'Arena Period: ' + ARENA_PERIOD_NAMES.get(self._periodType, 'Unknown')

    @classmethod
    def initParams(cls):
        return [InitParam('Period', SLOT_TYPE.E_ARENA_PERIOD, ARENA_PERIOD.BATTLE)]

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class ArenaPeriodStartEvent(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(ArenaPeriodStartEvent, self).__init__(*args, **kwargs)
        self._start = self._makeEventOutputSlot('start')
        self._update = self._makeEventOutputSlot('update')
        self._timeToEndSlot = self._makeDataOutputSlot('timeToEnd', SLOT_TYPE.FLOAT, self._execTimeToEnd)
        self._periodType = self._getInitParams()
        self.__periodTypeLast = None
        return

    @property
    def _arena(self):
        return getattr(BigWorld.player(), 'arena')

    @classmethod
    def blockIcon(cls):
        pass

    def captionText(self):
        return 'Arena Period Start: ' + ARENA_PERIOD_NAMES.get(self._periodType, 'Unknown')

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    @classmethod
    def initParams(cls):
        return [InitParam('Period', SLOT_TYPE.E_ARENA_PERIOD, ARENA_PERIOD.BATTLE)]

    def onStartScript(self):
        self.__subscribe()

    def onFinishScript(self):
        self.__unsubscribe()

    def _execTimeToEnd(self):
        arena = self._arena
        if arena is None or self._periodType != arena.period:
            self._timeToEndSlot.setValue(-1.0)
            return
        else:
            timeToEnd = max(0.0, arena.periodEndTime - BigWorld.serverTime())
            self._timeToEndSlot.setValue(timeToEnd)
            return

    def __subscribe(self):
        g_playerEvents.onArenaPeriodChange += self.__onPeriodChange

    def __unsubscribe(self):
        g_playerEvents.onArenaPeriodChange -= self.__onPeriodChange

    def __onPeriodChange(self, period, periodEndTime, periodLength, *args):
        if self._periodType != period:
            return
        if period == self.__periodTypeLast:
            self._update.call()
        else:
            self._start.call()
        self.__periodTypeLast = period


class OnBattleRoundFinished(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(OnBattleRoundFinished, self).__init__(*args, **kwargs)
        self._out = self._makeEventOutputSlot('onFinished')
        self._winner = self._makeDataOutputSlot('winnerTeam', SLOT_TYPE.INT, None)
        self._reason = self._makeDataOutputSlot('reason', SLOT_TYPE.E_FINISH_REASON, None)
        return

    @classmethod
    def blockIcon(cls):
        pass

    def onStartScript(self):
        g_playerEvents.onRoundFinished += self._onRoundFinished

    def onFinishScript(self):
        g_playerEvents.onRoundFinished -= self._onRoundFinished

    def _onRoundFinished(self, winnerTeam, reason, extraData):
        self._winner.setValue(winnerTeam)
        self._reason.setValue(reason)
        self._out.call()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class GetUDOByName(GetUDOByNameBase):
    _UDOTypes = [SLOT_TYPE.MARKER_POINT, SLOT_TYPE.AREA_TRIGGER]

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    def _getUDOsOfType(self, typeName):
        allUDOs = BigWorld.userDataObjects.values()
        return [ udo for udo in allUDOs if udo.__class__.__name__ == typeName ]


class GetArenaBorders(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(GetArenaBorders, self).__init__(*args, **kwargs)
        self._min = self._makeDataOutputSlot('min', SLOT_TYPE.VECTOR2, None)
        self._max = self._makeDataOutputSlot('max', SLOT_TYPE.VECTOR2, None)
        if not IS_VS_EDITOR:
            bbox = self._arena.arenaType.boundingBox
            self._min.setValue((bbox[0][0], bbox[0][1]))
            self._max.setValue((bbox[1][0], bbox[1][1]))
        return

    @property
    def _arena(self):
        return getattr(BigWorld.player(), 'arena')

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class GetVehicles(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(GetVehicles, self).__init__(*args, **kwargs)
        self._team = self._makeDataInputSlot('team', SLOT_TYPE.INT)
        self._excludePlayer = self._makeDataInputSlot('excludePlayer', SLOT_TYPE.BOOL)
        self._excludeDestroyed = self._makeDataInputSlot('excludeDestroyed', SLOT_TYPE.BOOL)
        self._vehicles = self._makeDataOutputSlot('vehicles', arrayOf(SLOT_TYPE.VEHICLE), self._execute)

    def _execute(self):
        if helpers.isPlayerAvatar():
            avatar = BigWorld.player()
            vehicles = avatar.vehicles
            team = self._team.getValue() if self._team.hasValue() else None
            if team is not None:
                vehicles = (v for v in vehicles if v.publicInfo.team == team)
            if self._excludePlayer.hasValue() and self._excludePlayer.getValue():
                vehicles = (v for v in vehicles if v.id != avatar.vehicle.id)
            if self._excludeDestroyed.hasValue() and self._excludeDestroyed.getValue():
                vehicles = (v for v in vehicles if v.isAlive())
            self._vehicles.setValue(map(weakref.proxy, vehicles))
        else:
            errorVScript(self, 'BigWorld.player is not player avatar.')
        return

    def validate(self):
        return super(GetVehicles, self).validate()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class GetDataFromStorage(GetDataFromStorageBase):

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    def _exec(self):
        self.arena = BigWorld.player().arena
        super(GetDataFromStorage, self)._exec()


class SetPrebattleCountdownTimerText(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(SetPrebattleCountdownTimerText, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')
        self._header = self._makeDataInputSlot('header', SLOT_TYPE.STR)
        self._subheader = self._makeDataInputSlot('subheader', SLOT_TYPE.STR)
        self._battleStartMessage = self._makeDataInputSlot('battleStartMessage', SLOT_TYPE.STR)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    def validate(self):
        if not self._header.hasValue():
            return 'header value is required.'
        return 'battleStartMessage value is required.' if not self._battleStartMessage.hasValue() else super(SetPrebattleCountdownTimerText, self).validate()

    def _execute(self):
        from gui.Scaleform.daapi.view.battle.shared.prebattle_timers.custom_text_timer import setTimerSettings
        if helpers.isPlayerAvatar():
            header = self._header.getValue()
            battleStartMessage = self._battleStartMessage.getValue()
            subheader = None
            if self._subheader.hasValue():
                subheader = self._subheader.getValue()
            setTimerSettings(header, battleStartMessage, subheader)
        else:
            errorVScript(self, 'BigWorld.player is not player avatar.')
        return


class CollideSegment(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(CollideSegment, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._collide)
        self._out = self._makeEventOutputSlot('out')
        self._spaceID = self._makeDataInputSlot('spaceId', SLOT_TYPE.INT)
        self._from = self._makeDataInputSlot('from', SLOT_TYPE.VECTOR3)
        self._to = self._makeDataInputSlot('to', SLOT_TYPE.VECTOR3)
        self._hitFlags = self._makeDataInputSlot('excludeHitFlags', SLOT_TYPE.INT)
        self._collision = self._makeDataOutputSlot('hasCollision', SLOT_TYPE.BOOL, None)
        self._collidePosition = self._makeDataOutputSlot('position', SLOT_TYPE.VECTOR3, None)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.HANGAR]

    def _collide(self):
        res = BigWorld.wg_collideSegment(self._spaceID.getValue(), self._from.getValue(), self._to.getValue(), self._hitFlags.getValue())
        collide = res is not None
        self._collision.setValue(collide)
        if collide:
            self._collidePosition.setValue(res.closestPoint)
        self._out.call()
        return


class GetControlPointPosition(Block, ArenaMeta):
    DELTA_Y = 500.0

    def __init__(self, *args, **kwargs):
        super(GetControlPointPosition, self).__init__(*args, **kwargs)
        self._controlPoint = self._makeDataInputSlot('controlPoint', SLOT_TYPE.CONTROL_POINT)
        self._position = self._makeDataOutputSlot('position', SLOT_TYPE.VECTOR3, self._execValue)

    def _execValue(self):
        if not (self._controlPoint.hasValue() and helpers.isPlayerAvatar()):
            self._position.setValue(Math.Vector3(0.0, 0.0, 0.0))
            return
        else:
            controlPoint = self._controlPoint.getValue()
            team, baseID = controlPoint.team, controlPoint.baseID
            controlPoints = g_cache[BigWorld.player().arenaTypeID].controlPoints
            teamBasePositions = g_cache[BigWorld.player().arenaTypeID].teamBasePositions
            if team == TEAMS_IN_ARENA.ANY_TEAM and controlPoints is not None:
                x, z = controlPoints[0]
            elif team <= len(teamBasePositions) and baseID in teamBasePositions[team - 1]:
                x, z = teamBasePositions[team - 1][baseID]
            else:
                self._position.setValue(Math.Vector3(0.0, 0.0, 0.0))
                return
            testRes = BigWorld.wg_collideSegment(BigWorld.player().spaceID, Math.Vector3(x, self.DELTA_Y, z), Math.Vector3(x, -self.DELTA_Y, z), CollisionFlags.TRIANGLE_NOCOLLIDE)
            if testRes is None:
                self._position.setValue(Math.Vector3(0.0, 0.0, 0.0))
            else:
                self._position.setValue(testRes.closestPoint)
            return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    @classmethod
    def blockIcon(cls):
        pass
