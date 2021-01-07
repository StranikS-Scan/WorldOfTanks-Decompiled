# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/hints/HintsShoot.py
import time
import math
import TriggersManager
import BigWorld
from bootcamp.BootcampConstants import HINT_TYPE
from bootcamp_shared import BOOTCAMP_BATTLE_ACTION
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from HintsBase import HINT_COMMAND, HintBase
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class HintAim(HintBase, TriggersManager.ITriggerListener):

    def __init__(self, avatar, params):
        super(HintAim, self).__init__(avatar, HINT_TYPE.HINT_AIM, 0)
        self.__aimFactor = params.get('aimFactor')
        self.__maxAimlessShootCount = params.get('shootCount')
        self.__curAimlessShootCount = 0
        self.__timeOnScreen = params['timeout']

    def update(self):
        command = None
        if self._state == HintBase.STATE_DEFAULT:
            if self.__curAimlessShootCount >= self.__maxAimlessShootCount:
                command = HINT_COMMAND.SHOW
                self._state = HintBase.STATE_HINT
                self.__curAimlessShootCount = 0
                self.__timeAppearOnScreen = time.time()
        elif self._state == HintBase.STATE_HINT:
            if time.time() - self.__timeAppearOnScreen > self.__timeOnScreen:
                self._state = HintBase.STATE_DEFAULT
                command = HINT_COMMAND.HIDE
        return command

    def start(self):
        self._state = HintBase.STATE_DEFAULT
        TriggersManager.g_manager.addListener(self)

    def stop(self):
        self._state = HintBase.STATE_INACTIVE
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delListener(self)
        return

    def onTriggerActivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.PLAYER_SHOOT:
            markerSize = self._avatar.gunRotator.markerInfo[2]
            LOG_DEBUG_DEV_BOOTCAMP('PLAYER_SHOOT, markerSize - ', markerSize)
            if self.__aimFactor < markerSize:
                self.__curAimlessShootCount += 1
            else:
                self.__curAimlessShootCount = 0


class HintTargetUnLock(HintBase):

    def __init__(self, avatar, params):
        super(HintTargetUnLock, self).__init__(avatar, HINT_TYPE.HINT_UNLOCK_TARGET, params.get('timeout', -1.0))
        self.__lockTarget = False
        self.__targetID = -1

    def start(self):
        TriggersManager.g_manager.addListener(self)

    def stop(self):
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delListener(self)
        return

    def update(self):
        resultCommand = None
        if self._state == HintBase.STATE_INACTIVE:
            if self.__lockTarget:
                self._state = HintBase.STATE_HINT
                resultCommand = HINT_COMMAND.SHOW
        elif self._state == HintBase.STATE_HINT:
            if not self.__lockTarget:
                self._state = HintBase.STATE_DEFAULT
                resultCommand = HINT_COMMAND.HIDE
        elif self._state == HintBase.STATE_DEFAULT:
            if self.__lockTarget:
                self._state = HintBase.STATE_HINT
                resultCommand = HINT_COMMAND.SHOW
        return resultCommand

    def onTriggerActivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE:
            self.__lockTarget = True
            self.__targetID = args['vehicleId']

    def onTriggerDeactivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE:
            self.__lockTarget = False
            self.__targetID = -1


class HintSecondarySniper(HintBase, TriggersManager.ITriggerListener):

    def __init__(self, avatar, params):
        super(HintSecondarySniper, self).__init__(avatar, HINT_TYPE.HINT_SECONDARY_SNIPER, params['timeout'])
        self.__distance = params['distance']
        self.__shootInTarget = False
        self.__angle = params['angle']
        self.__timeHintShown = 0.0
        self.__inSniperMode = False
        self.__sniperTriggerId = None
        return

    def start(self):
        self._state = HintBase.STATE_DEFAULT
        self.__sniperTriggerId = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.SNIPER_MODE)
        TriggersManager.g_manager.addListener(self)

    def stop(self):
        self._state = HintBase.STATE_INACTIVE
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delTrigger(self.__sniperTriggerId)
            TriggersManager.g_manager.delListener(self)
        return

    def update(self):
        if self._state == HintBase.STATE_DEFAULT:
            if self.__shootInTarget:
                self.__timeHintShown = time.time()
                self._state = HintBase.STATE_HINT
                return HINT_COMMAND.SHOW
        elif self._state == HintBase.STATE_HINT:
            if self._timeout < time.time() - self.__timeHintShown:
                self.__shootInTarget = False
                self._state = HintBase.STATE_DEFAULT
                return HINT_COMMAND.HIDE

    def isShootingInEnemy(self, shootVector):
        for vehicle in self._avatar.vehicles:
            if self._avatar.arena.vehicles[vehicle.id]['team'] != self._avatar.team and vehicle.isAlive():
                position = vehicle.position
                playerPosition = BigWorld.entity(self._avatar.playerVehicleID).position
                direction = position - playerPosition
                direction.normalise()
                cosAlpha = shootVector.dot(direction)
                if cosAlpha > math.cos(self.__angle) and playerPosition.flatDistTo(position) > self.__distance:
                    return True

        return False

    def onTriggerActivated(self, args):
        triggerType = args['type']
        if triggerType == TriggersManager.TRIGGER_TYPE.SNIPER_MODE:
            self.__inSniperMode = True
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_SHOOT:
            if not self.__inSniperMode:
                _, shotVector = self._avatar.gunRotator.getCurShotPosition()
                shotVector.normalise()
                if self.isShootingInEnemy(shotVector):
                    self.__shootInTarget = True

    def onTriggerDeactivated(self, args):
        triggerType = args['type']
        if triggerType == TriggersManager.TRIGGER_TYPE.SNIPER_MODE:
            self.__inSniperMode = False


class HintWaitReload(HintBase, TriggersManager.ITriggerListener):

    def __init__(self, avatar, params):
        super(HintWaitReload, self).__init__(avatar, HINT_TYPE.HINT_WAIT_RELOAD, params['timeout'])
        self.__numShootingErrors = 0
        self.__maxShootingErrors = params.get('maxShootErrorsCount', 3)

    def start(self):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        ctrl = sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowVehicleErrorByKey += self.__onShowVehicleErrorByKey
        self._state = HintBase.STATE_DEFAULT
        TriggersManager.g_manager.addListener(self)
        return

    def stop(self):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        ctrl = sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowVehicleErrorByKey -= self.__onShowVehicleErrorByKey
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delListener(self)
        self._state = HintBase.STATE_INACTIVE
        return

    def update(self):
        resultCommand = None
        if self._state == HintBase.STATE_DEFAULT:
            if self.__numShootingErrors >= self.__maxShootingErrors:
                self._timeStart = time.time()
                self._state = HintBase.STATE_HINT
                resultCommand = HINT_COMMAND.SHOW
        elif self._state == HintBase.STATE_HINT:
            if self._timeout < time.time() - self._timeStart:
                self._state = HintBase.STATE_DEFAULT
                resultCommand = HINT_COMMAND.HIDE
        return resultCommand

    def __onShowVehicleErrorByKey(self, key, args=None, extra=None):
        if key == 'cantShootGunReloading' and self._state == HintBase.STATE_DEFAULT:
            self.__numShootingErrors += 1

    def onTriggerActivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.PLAYER_SHOOT:
            self.__numShootingErrors = 0

    def onTriggerDeactivated(self, args):
        pass


class HintShootWhileMoving(HintBase, TriggersManager.ITriggerListener):

    def __init__(self, avatar, params):
        super(HintShootWhileMoving, self).__init__(avatar, HINT_TYPE.HINT_SHOT_WHILE_MOVING, params['timeout'])
        self.__showHint = False
        self.__moving = False
        self.__timeHintShown = 0.0
        self.__maxShootErrorsCount = params['maxShootErrorsCount']
        self.__errorsLeft = self.__maxShootErrorsCount

    def start(self):
        self._state = HintBase.STATE_DEFAULT
        self.__missTriggerId = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_MISSED)
        TriggersManager.g_manager.addListener(self)

    def stop(self):
        self._state = HintBase.STATE_INACTIVE
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delTrigger(self.__missTriggerId)
            TriggersManager.g_manager.delListener(self)
        return

    def update(self):
        if self._state == HintBase.STATE_DEFAULT:
            if self.__showHint:
                self.__timeHintShown = time.time()
                self.__showHint = False
                self.__resetErrorsCount()
                self._state = HintBase.STATE_HINT
                return HINT_COMMAND.SHOW
        elif self._state == HintBase.STATE_HINT:
            if time.time() - self.__timeHintShown > self._timeout:
                self._state = HintBase.STATE_DEFAULT
                return HINT_COMMAND.HIDE
        return None

    def __resetErrorsCount(self):
        self.__errorsLeft = self.__maxShootErrorsCount

    def onAction(self, actionId, actionParams):
        if actionId == BOOTCAMP_BATTLE_ACTION.PLAYER_MOVE:
            flags = actionParams[0]
            self.__moving = bool(flags & 2 or flags & 1)
            if not self.__moving:
                self.__resetErrorsCount()
        elif actionId == BOOTCAMP_BATTLE_ACTION.PLAYER_HIT_VEHICLE:
            self.__resetErrorsCount()

    def onTriggerActivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_MISSED:
            if self.__moving:
                self.__errorsLeft = self.__errorsLeft - 1
                if self.__errorsLeft == 0 and self._state == HintBase.STATE_DEFAULT:
                    self.__showHint = True

    def onTriggerDeactivated(self, args):
        pass
