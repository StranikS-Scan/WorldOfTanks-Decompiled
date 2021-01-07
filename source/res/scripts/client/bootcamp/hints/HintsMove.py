# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/hints/HintsMove.py
import time
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampConstants import HINT_TYPE
from bootcamp_shared import BOOTCAMP_BATTLE_ACTION
from HintsBase import HintBase, HINT_COMMAND

class HintNoMove(HintBase):

    def __init__(self, avatar, params):
        super(HintNoMove, self).__init__(avatar, HINT_TYPE.HINT_NO_MOVE, params['timeout'])
        self.__seconds = params['seconds']
        self.__lastMoveTime = 0.0
        self.__timeHintShown = 0.0

    def start(self):
        self._timeStart = time.time()
        self._state = HintBase.STATE_DEFAULT
        self.__lastMoveTime = time.time()
        g_bootcampEvents.onBattleAction += self.__onBattleAction

    def stop(self):
        g_bootcampEvents.onBattleAction -= self.__onBattleAction
        self._state = HintBase.STATE_INACTIVE

    def __onBattleAction(self, actionId, actionArgs):
        if actionId == BOOTCAMP_BATTLE_ACTION.PLAYER_MOVE:
            flags = actionArgs[0]
            if flags > 0:
                self.__lastMoveTime = time.time()

    def update(self):
        if self._state == HintBase.STATE_INACTIVE:
            return
        else:
            resultCommand = None
            if self._state == HintBase.STATE_DEFAULT:
                if self.__seconds < time.time() - self.__lastMoveTime:
                    self.__timeHintShown = time.time()
                    self._state = HintBase.STATE_HINT
                    resultCommand = HINT_COMMAND.SHOW
            elif self._state == HintBase.STATE_HINT:
                if self._timeout < time.time() - self.__timeHintShown:
                    self._state = HintBase.STATE_DEFAULT
                    resultCommand = HINT_COMMAND.HIDE
            return resultCommand


class HintNoMoveTurret(HintBase):

    def __init__(self, avatar, params):
        super(HintNoMoveTurret, self).__init__(avatar, HINT_TYPE.HINT_NO_MOVE_TURRET, params['timeout'])
        self.__seconds = params['seconds']
        self.__lastMoveTime = 0.0
        self.__lastTurretVector = None
        self.__timeHintShown = 0.0
        return

    def start(self):
        self._state = HintBase.STATE_DEFAULT
        self.__lastMoveTime = time.time()

    def stop(self):
        self._state = HintBase.STATE_INACTIVE

    def update(self):
        if self._state == HintBase.STATE_INACTIVE:
            return
        elif self.__lastTurretVector is None:
            _, self.__lastTurretVector = self._avatar.gunRotator.getCurShotPosition()
            self.__lastTurretVector.normalise()
            return
        else:
            _, shotVector = self._avatar.gunRotator.getCurShotPosition()
            shotVector.normalise()
            cosAngle = shotVector.dot(self.__lastTurretVector)
            self.__lastTurretVector = shotVector
            if cosAngle < 0.9999:
                self.__lastMoveTime = time.time()
            resultCommand = None
            if self._state == HintBase.STATE_DEFAULT:
                if self.__seconds < time.time() - self.__lastMoveTime:
                    self.__timeHintShown = time.time()
                    self._state = HintBase.STATE_HINT
                    resultCommand = HINT_COMMAND.SHOW
            elif self._state == HintBase.STATE_HINT:
                if self.__seconds < time.time() - self.__timeHintShown:
                    self._state = HintBase.STATE_DEFAULT
                    resultCommand = HINT_COMMAND.HIDE
            return resultCommand


class HintMoveToMarker(HintBase):

    def __init__(self, avatar, params):
        super(HintMoveToMarker, self).__init__(avatar, HINT_TYPE.HINT_MOVE_TO_MARKER, params['timeout'])
        self.__distance = params.get('maxDistance', 30.0)
        self.__lastMarker = None
        self.__lastMarkerPosition = None
        self.__minLastMarkerDistance = 0.0
        self.__markers = None
        return

    def start(self):
        self._timeStart = time.time()
        self._state = HintBase.STATE_INACTIVE

    def stop(self):
        self._state = HintBase.STATE_INACTIVE
        self.__markers = None
        self.__lastMarker = None
        return

    def update(self):
        if self._state == HintBase.STATE_INACTIVE:
            return
        else:
            self.updateLastMarker()
            distanceToMarker = None
            if self.__lastMarker is not None:
                distanceToMarker = self._avatar.position.distTo(self.__lastMarkerPosition)
                if distanceToMarker < self.__minLastMarkerDistance:
                    self.__minLastMarkerDistance = distanceToMarker
            resultCommand = None
            if self._state == HintBase.STATE_DEFAULT:
                if self.__lastMarker is not None and distanceToMarker is not None and distanceToMarker - self.__minLastMarkerDistance > self.__distance:
                    self._state = HintBase.STATE_HINT
                    resultCommand = HINT_COMMAND.SHOW
            elif self._state == HintBase.STATE_HINT:
                if self.__lastMarker is None or distanceToMarker is not None and distanceToMarker - self.__minLastMarkerDistance < self.__distance:
                    self._state = HintBase.STATE_DEFAULT
                    resultCommand = HINT_COMMAND.HIDE
            return resultCommand

    def updateLastMarker(self):
        markers = self.__markers.getActiveMarkers().values()
        if len(markers) == 1:
            marker = markers[0]
            if marker != self.__lastMarker or self.__lastMarker is None:
                self.__lastMarker = marker
                self.__lastMarkerPosition = self.__lastMarker.position
                self.__minLastMarkerDistance = self._avatar.position.distTo(self.__lastMarkerPosition)
        else:
            self.__lastMarker = None
        return
