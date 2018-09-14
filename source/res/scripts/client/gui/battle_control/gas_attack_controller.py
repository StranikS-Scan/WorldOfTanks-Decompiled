# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/gas_attack_controller.py
from collections import namedtuple
import BigWorld
import math
import Math
import Event
from GasAttackSettings import GasAttackState, gasAttackStateFor
from constants import DEATH_ZONES
from gui.Scaleform.daapi.view.battle.indicators import createDirectIndicatorMessage
from gui.Scaleform.locale.FALLOUT import FALLOUT
from gui.battle_control import arena_info
from helpers import time_utils
from Math import Vector3
from shared_utils import makeTupleByDict
_WARNING_DISTANCE = 30

class GAS_ATTACK_STATE(object):
    NO_ATTACK = 0
    PREPEARING = 1
    INSIDE_SAFE_ZONE = 2
    NEAR_SAFE = 3
    NEAR_CLOUD = 4
    INSIDE_CLOUD = 5
    DEAD = 6
    VISIBLE = (NEAR_SAFE, NEAR_CLOUD, INSIDE_CLOUD)


_GasAttackState = namedtuple('_GasAttackState', ('state', 'prevState', 'center', 'currentRadius', 'safeZoneRadius', 'centerDistance', 'safeZoneDistance', 'gasCloudDistance', 'timeLeft'))
_GasAttackState.__new__.__defaults__ = (GAS_ATTACK_STATE.NO_ATTACK,
 GAS_ATTACK_STATE.NO_ATTACK,
 0,
 Vector3(0, 0, 0),
 0,
 0,
 0,
 0,
 0)

class GasAttackController(object):

    def __init__(self, ctx):
        super(GasAttackController, self).__init__()
        self.__state = _GasAttackState()
        self.__gasAttackMgr = ctx.gasAttackMgr
        self.__battleUI = None
        self.__falloutItems = None
        self.__indicatorUI = None
        self.__timerCallback = None
        self.__settings = None
        self.__evtManager = Event.EventManager()
        self.onPreparing = Event.Event(self.__evtManager)
        self.onStarted = Event.Event(self.__evtManager)
        self.onUpdated = Event.Event(self.__evtManager)
        self.onEnded = Event.Event(self.__evtManager)
        return

    def start(self, battleUI):
        self.__battleUI = battleUI
        self.__falloutItems = battleUI.movie.falloutItems
        self.__settings = arena_info.getGasAttackSettings()
        self.__gasAttackMgr.onAttackPreparing += self.__onAttackPreparing
        self.__gasAttackMgr.onAttackStarted += self.__onAttackStarted
        self.__gasAttackMgr.onAttackStopped += self.__onAttackStopped
        self.updateState()
        self.__startTimer()

    def stop(self):
        self.__state = None
        self.__battleUI = None
        self.__falloutItems = None
        self.__settings = None
        self.__stopTimer()
        self.__finiIndicator()
        if self.__gasAttackMgr is not None:
            self.__gasAttackMgr.onAttackPreparing -= self.__onAttackPreparing
            self.__gasAttackMgr.onAttackStarted -= self.__onAttackStarted
            self.__gasAttackMgr.onAttackStopped -= self.__onAttackStopped
            self.__gasAttackMgr = None
        self.__evtManager.clear()
        return

    def clear(self):
        pass

    def updateState(self):
        params = {}
        if self.__gasAttackMgr.state == GasAttackState.PREPARE:
            params['state'] = GAS_ATTACK_STATE.PREPEARING
            params['prevState'] = self.__state.state
            params['center'] = self.__gasAttackMgr.settings.position
            params['timeLeft'] = self.__getTimeLeft()
        elif self.__gasAttackMgr.state in (GasAttackState.ATTACK, GasAttackState.DONE):
            centerDistance = self.__getCenterDistance()
            currentRadius = self.__getCurrentRadius()
            cloudDistance = self.__getCloudDistance(currentRadius)
            safeZoneDistance = self.__getSafeZoneDistance()
            if not BigWorld.player().isVehicleAlive:
                state = GAS_ATTACK_STATE.DEAD
            elif safeZoneDistance == 0:
                state = GAS_ATTACK_STATE.INSIDE_SAFE_ZONE
            elif cloudDistance == 0:
                state = GAS_ATTACK_STATE.INSIDE_CLOUD
            elif cloudDistance <= _WARNING_DISTANCE:
                state = GAS_ATTACK_STATE.NEAR_CLOUD
            else:
                state = GAS_ATTACK_STATE.NEAR_SAFE
            params['state'] = state
            params['prevState'] = self.__state.state
            params['center'] = self.__gasAttackMgr.settings.position
            params['timeLeft'] = self.__getTimeLeft()
            params['currentRadius'] = currentRadius
            params['safeZoneRadius'] = self.__gasAttackMgr.settings.endRadius
            params['centerDistance'] = centerDistance
            params['safeZoneDistance'] = safeZoneDistance
            params['gasCloudDistance'] = cloudDistance
        self.__state = makeTupleByDict(_GasAttackState, params)

    def updateUI(self):
        self.onUpdated(self.__state)

    def __onAttackPreparing(self):
        self.__initIndicator()
        self.updateState()
        self.__updateBattleGasItems()
        self.onPreparing(self.__state)

    def __onAttackStarted(self):
        self.__initIndicator()
        self.updateState()
        self.onStarted(self.__state)
        self.__startTimer()

    def __onAttackStopped(self):
        self.clear()
        self.onEnded(self.__state)

    def __initIndicator(self):
        if self.__indicatorUI is None:
            self.__indicatorUI = createDirectIndicatorMessage()
            self.__indicatorUI.track(self.__settings.position)
            self.__indicatorUI.setMessage(FALLOUT.SAFEZONEDIRECTION_MESSAGE)
            self.__indicatorUI.setVisibility(False)
        return

    def __updateIndicator(self):
        isVisible = self.__state.state in GAS_ATTACK_STATE.VISIBLE
        if self.__indicatorUI is not None:
            self.__indicatorUI.setVisibility(isVisible)
            if isVisible:
                self.__indicatorUI.setDistance(self.__state.safeZoneDistance)
        return

    def __finiIndicator(self):
        if self.__indicatorUI is not None:
            self.__indicatorUI.remove()
            self.__indicatorUI = None
        return

    def __updateDeathZoneIndicator(self):
        if self.__battleUI is not None and self.__state.state != self.__state.prevState:
            if self.__state.state == GAS_ATTACK_STATE.NEAR_CLOUD:
                self.__battleUI.showDeathzoneTimer((DEATH_ZONES.GAS_ATTACK, -1, 'warning'))
            elif self.__state.state != GAS_ATTACK_STATE.INSIDE_CLOUD:
                self.__battleUI.hideDeathzoneTimer(DEATH_ZONES.GAS_ATTACK)
        return

    def __startTimer(self):
        if self.__state.state not in (GAS_ATTACK_STATE.NO_ATTACK, GAS_ATTACK_STATE.PREPEARING):
            self.__updateIndicator()
            self.__updateDeathZoneIndicator()
            self.__updateBattleGasItems()
            self.onUpdated(self.__state)
            if self.__state.timeLeft > 0:
                self.__timerCallback = BigWorld.callback(1, self.__processTimer)
        else:
            self.__stopTimer()

    def __updateBattleGasItems(self):
        isSafeZoneTimerVisible = self.__state.state == GAS_ATTACK_STATE.NEAR_SAFE
        minimapGasIsVisible = self.__state.state != GAS_ATTACK_STATE.PREPEARING
        timeStr = time_utils.getTimeLeftFormat(self.__state.timeLeft)
        self.__falloutItems.as_gasAtackUpdate(self.__state.state, minimapGasIsVisible, self.__state.currentRadius, isSafeZoneTimerVisible, timeStr)

    def __processTimer(self):
        self.__timerCallback = None
        self.updateState()
        self.__startTimer()
        return

    def __stopTimer(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        return

    def __getTimeLeft(self):
        attackEndTime = self.__gasAttackMgr.startTime + self.__gasAttackMgr.settings.attackLength
        return max(0, attackEndTime - BigWorld.serverTime())

    def __getCenterDistance(self):
        vehicleMatrix = BigWorld.player().consistentMatrices.attachedVehicleMatrix
        if BigWorld.player().isVehicleAlive and vehicleMatrix is not None:
            x0, y0, z0 = self.__settings.position
            x1, y1, z1 = Math.Matrix(vehicleMatrix).translation
            return math.sqrt(math.pow(x0 - x1, 2) + math.pow(z0 - z1, 2) + math.pow(y0 - y1, 2))
        else:
            return 0

    def __getSafeZoneDistance(self):
        return max(0, self.__getCenterDistance() - self.__settings.endRadius)

    def __getCurrentRadius(self):
        timeFromActivation = max(0, BigWorld.serverTime() - self.__gasAttackMgr.startTime)
        _, (_, currentRadius) = gasAttackStateFor(self.__settings, timeFromActivation)
        return currentRadius

    def __getCloudDistance(self, currentRadius):
        return max(0, currentRadius - self.__getCenterDistance())
