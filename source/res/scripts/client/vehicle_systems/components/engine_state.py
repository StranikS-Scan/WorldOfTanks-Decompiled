# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/engine_state.py
from random import uniform
import BigWorld
from constants import ARENA_PERIOD

class EngineState(object):
    NORMAL = 0
    REPAIRED = 1
    CRITICAL = 2
    DESTROYED = 3


class EngineLoad(object):
    _STOPPED = 0
    _IDLE = 1
    _MEDIUM = 2
    _HIGH = 3


_StateConvertor = {'destroyed': EngineState.DESTROYED,
 'critical': EngineState.CRITICAL,
 'repaired': EngineState.REPAIRED,
 'normal': EngineState.NORMAL}

def getEngineStateFromName(stateName):
    return _StateConvertor.get(stateName, EngineState.NORMAL)


def checkEngineStart(detailedEngineState, period):
    if period == ARENA_PERIOD.PREBATTLE:
        notifyEngineOnArenaPeriodChange(detailedEngineState, period)
    elif period == ARENA_PERIOD.BATTLE:
        detailedEngineState.startEngineWithDelay(0.1)


def notifyEngineOnArenaPeriodChange(detailedEngineState, period):
    if period == ARENA_PERIOD.PREBATTLE:
        periodEndTime = BigWorld.player().arena.periodEndTime
        serverTime = BigWorld.serverTime()
        maxTime = periodEndTime - serverTime
        maxTime = maxTime * 0.7 if maxTime > 0.0 else 1.0
        time = uniform(0.0, maxTime)
        detailedEngineState.startEngineWithDelay(time)
