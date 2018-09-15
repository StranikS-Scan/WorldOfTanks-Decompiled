# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/hints/HintsShoot.py
import time
import TriggersManager
import math
import Math
import BigWorld
from bootcamp.BootcampConstants import HINT_TYPE
from bootcamp_shared import BOOTCAMP_BATTLE_ACTION
from debug_utils_bootcamp import LOG_CURRENT_EXCEPTION_BOOTCAMP, LOG_DEBUG_DEV_BOOTCAMP
from HintsBase import HINT_COMMAND, HintBase
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class HintSniper(HintBase, TriggersManager.ITriggerListener):

    def __init__(self, avatar, params=None):
        super(HintSniper, self).__init__(avatar, HINT_TYPE.HINT_SNIPER, 0)
        self.__switchedToSniperMode = False
        self.__sniperTriggerId = None
        return

    def update(self):
        if self._state != HintBase.STATE_COMPLETE and self.__switchedToSniperMode:
            self._state = HintBase.STATE_COMPLETE
            return HINT_COMMAND.SHOW_COMPLETED
        else:
            return None

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

    def onTriggerActivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.SNIPER_MODE:
            self.__switchedToSniperMode = True


class HintSniperLevel0(HintSniper):

    def __init__(self, avatar, params=None):
        super(HintSniperLevel0, self).__init__(avatar, params)
        self.typeId = HINT_TYPE.HINT_SNIPER_LEVEL0


class HintShoot(HintBase):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, avatar, params):
        super(HintShoot, self).__init__(avatar, HINT_TYPE.HINT_SHOOT, params['timeout'])
        self.__detectedEnemy = False
        self.__shootedEnemy = False
        self.__enemies = [ vehId for vehId, vehInfo in self._avatar.arena.vehicles.items() if vehInfo['team'] != avatar.team ]

    def update(self):
        resultCommand = None
        if self._state == HintBase.STATE_INACTIVE:
            if self.__detectedEnemy:
                self._timeStart = time.time()
                self._state = HintBase.STATE_HINT
                resultCommand = HINT_COMMAND.SHOW
        elif self._state == HintBase.STATE_HINT:
            if self.__shootedEnemy:
                self._state = HintBase.STATE_COMPLETE
                resultCommand = HINT_COMMAND.SHOW_COMPLETED_WITH_HINT
        elif self._state == HintBase.STATE_DEFAULT:
            if self.__shootedEnemy:
                self._state = HintBase.STATE_COMPLETE
                resultCommand = HINT_COMMAND.SHOW_COMPLETED
        return resultCommand

    def onAction(self, actionId, actionParams):
        if actionId == BOOTCAMP_BATTLE_ACTION.PLAYER_HIT_VEHICLE:
            assert actionParams
            vehicleId = actionParams[0]
            if vehicleId in self.__enemies:
                self.__shootedEnemy = True

    def onTriggerActivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.PLAYER_DETECT_ENEMY:
            isVisible = args['isVisible']
            isDirect = args['isDirect']
            targetId = args['targetId']
            if isVisible and isDirect and targetId in self.__enemies:
                self.__detectedEnemy = True

    def onTriggerDeactivated(self, args):
        pass

    def start(self):
        TriggersManager.g_manager.addListener(self)

    def stop(self):
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delListener(self)
        return


class HintAdvancedSniper(HintBase, TriggersManager.ITriggerListener):
    STATE_DEFAULT_SNIPER = 0
    STATE_HINT_SNIPER = 1
    STATE_COMPLETE_SNIPER = 2
    STATE_HINT_WEAK_POINTS = 3
    STATE_VEHICLE_KILLED = 4
    STATE_EXIT_SNIPER_MODE = 5
    STATE_INACTIVE = 6

    @property
    def message(self):
        if self._state == HintAdvancedSniper.STATE_HINT_SNIPER:
            return self.__messageSniperBefore
        return self.__messageSniperExit if self._state == HintAdvancedSniper.STATE_EXIT_SNIPER_MODE else self.__message

    @message.setter
    def message(self, message):
        self.__message = message

    @property
    def voiceover(self):
        if self._state == self.STATE_HINT_SNIPER:
            return self.__voiceoverEnterSniper
        return self.__voiceoverWeakPoints if self._state == self.STATE_HINT_WEAK_POINTS else self.__voiceoverExitSniper

    def __init__(self, avatar, params):
        super(HintAdvancedSniper, self).__init__(avatar, HINT_TYPE.HINT_SNIPER, 0)
        self.__vehicleWasKilled = False
        self.__inSniperMode = False
        targetName = params['target_name']
        self.__targetVehicleId = None
        for vehId, vehInfo in self._avatar.arena.vehicles.iteritems():
            if vehInfo['name'] == targetName:
                self.__targetVehicleId = vehId
                break

        self.__angle = math.radians(params.get('angle', 15.0))
        self.__cooldownAfterAll = 0.0
        self.__timeBetween = params['time_between']
        self.__messageSniperBefore = params['message_sniper_before']
        self.__messageSniperExit = params['message_sniper_exit']
        self.__voiceoverEnterSniper = params['enter_voiceover']
        self.__voiceoverExitSniper = params['exit_voiceover']
        self.__voiceoverWeakPoints = params['weak_points_voiceover']
        return

    def start(self):
        self._state = HintAdvancedSniper.STATE_DEFAULT_SNIPER
        self._avatar.arena.onVehicleKilled += self.__onVehicleKilled
        self.__cooldownAfterAll = self.cooldownAfter
        self.cooldownAfter = self.__timeBetween
        self.__sniperTriggerId = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.SNIPER_MODE)
        TriggersManager.g_manager.addListener(self)

    def stop(self):
        self._state = HintAdvancedSniper.STATE_INACTIVE
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delTrigger(self.__sniperTriggerId)
            TriggersManager.g_manager.delListener(self)
        return

    def update(self):
        if self._state == HintAdvancedSniper.STATE_INACTIVE:
            return
        else:
            resultCommand = None
            targetVehicle = self.__getVehicleTarget()
            if self._state == HintAdvancedSniper.STATE_DEFAULT_SNIPER:
                if targetVehicle is not None:
                    if self.__inSniperMode:
                        self._state = HintAdvancedSniper.STATE_COMPLETE_SNIPER
                    else:
                        resultCommand = HINT_COMMAND.SHOW
                        self._state = HintAdvancedSniper.STATE_HINT_SNIPER
                elif self.__vehicleWasKilled:
                    if self.__inSniperMode:
                        self._state = HintAdvancedSniper.STATE_VEHICLE_KILLED
                    else:
                        self._state = HintAdvancedSniper.STATE_INACTIVE
            elif self._state == HintAdvancedSniper.STATE_HINT_SNIPER:
                if targetVehicle is not None:
                    if self.__inSniperMode:
                        self._state = HintAdvancedSniper.STATE_COMPLETE_SNIPER
                        resultCommand = HINT_COMMAND.HIDE
                else:
                    if self.__vehicleWasKilled:
                        self._state = HintAdvancedSniper.STATE_VEHICLE_KILLED
                    else:
                        self._state = HintAdvancedSniper.STATE_DEFAULT_SNIPER
                    resultCommand = HINT_COMMAND.HIDE
            elif self._state == HintAdvancedSniper.STATE_COMPLETE_SNIPER:
                if self.__vehicleWasKilled:
                    self._state = HintAdvancedSniper.STATE_VEHICLE_KILLED
                else:
                    self._state = HintAdvancedSniper.STATE_HINT_WEAK_POINTS
                    self.cooldownAfter = self.__cooldownAfterAll
                    self.typeId = HINT_TYPE.HINT_WEAK_POINTS
                    resultCommand = HINT_COMMAND.SHOW
            elif self._state == HintAdvancedSniper.STATE_HINT_WEAK_POINTS:
                if self.__vehicleWasKilled:
                    self._state = HintAdvancedSniper.STATE_VEHICLE_KILLED
                    self.cooldownAfter = self.__timeBetween
                    resultCommand = HINT_COMMAND.HIDE
                elif targetVehicle is None or not self.__inSniperMode:
                    self._state = HintAdvancedSniper.STATE_DEFAULT_SNIPER
                    self.cooldownAfter = self.__timeBetween
                    self.typeId = HINT_TYPE.HINT_SNIPER
                    resultCommand = HINT_COMMAND.HIDE
            elif self._state == HintAdvancedSniper.STATE_VEHICLE_KILLED:
                if self.__inSniperMode:
                    self._state = HintAdvancedSniper.STATE_EXIT_SNIPER_MODE
                    self.typeId = HINT_TYPE.HINT_SNIPER
                    resultCommand = HINT_COMMAND.SHOW
                else:
                    self._state = HintAdvancedSniper.STATE_INACTIVE
                    self.cooldownAfter = self.__cooldownAfterAll
            elif self._state == HintAdvancedSniper.STATE_EXIT_SNIPER_MODE:
                if not self.__inSniperMode:
                    resultCommand = HINT_COMMAND.HIDE
                    self.cooldownAfter = self.__cooldownAfterAll
                    self._state = HintAdvancedSniper.STATE_INACTIVE
            return resultCommand

    def onTriggerActivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.SNIPER_MODE:
            self.__inSniperMode = True

    def onTriggerDeactivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.SNIPER_MODE:
            self.__inSniperMode = False

    def __onVehicleKilled(self, targetID, attackerID, *args):
        if self.__targetVehicleId == targetID:
            self.__vehicleWasKilled = True

    def __getVehicleTarget(self):
        for vehicle in self._avatar.vehicles:
            if vehicle.id != self.__targetVehicleId:
                continue
            if not vehicle.isAlive():
                return None
            if self.__isDirInShootingAngle(vehicle):
                return vehicle
            return None

        return None

    def __isDirInShootingAngle(self, vehicle):
        _, shotVector = self._avatar.gunRotator.getCurShotPosition()
        shotVector.normalise()
        position = vehicle.position
        playerPosition = BigWorld.entity(self._avatar.playerVehicleID).position
        direction = position - playerPosition
        direction.normalise()
        cosAlpha = shotVector.dot(direction)
        return cosAlpha > math.cos(self.__angle)


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


class HintTargetLock(HintBase):

    def __init__(self, avatar, params):
        super(HintTargetLock, self).__init__(avatar, HINT_TYPE.HINT_TARGET_LOCK, params.get('timeout', 3.0))
        self.__detectedEnemy = False
        self.__shootedEnemy = False
        self.__lockTarget = False
        self.__vehicleWasKilled = False
        self.__enemies = [ vehId for vehId, vehInfo in avatar.arena.vehicles.items() if vehInfo['name'] in params.get('names', []) ]
        self.__lockTriggerId = None
        return

    def start(self):
        TriggersManager.g_manager.addListener(self)
        self.__lockTriggerId = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE)
        self._avatar.arena.onVehicleKilled += self.__onVehicleKilled

    def stop(self):
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delTrigger(self.__lockTriggerId)
            TriggersManager.g_manager.delListener(self)
        return

    def update(self):
        resultCommand = None
        if self._state == HintBase.STATE_INACTIVE:
            if self.__shootedEnemy:
                self._timeStart = time.time()
                self._state = HintBase.STATE_HINT
                resultCommand = HINT_COMMAND.SHOW
        elif self._state == HintBase.STATE_HINT:
            if self.__vehicleWasKilled:
                self._state = HintBase.STATE_DEFAULT
                resultCommand = HINT_COMMAND.HIDE
            elif self.__lockTarget:
                self._state = HintBase.STATE_COMPLETE
                resultCommand = HINT_COMMAND.SHOW_COMPLETED_WITH_HINT
        elif self._state == HintBase.STATE_DEFAULT:
            if self.__lockTarget:
                self._state = HintBase.STATE_COMPLETE
                resultCommand = HINT_COMMAND.SHOW_COMPLETED
                if self.__suppressSuccess:
                    resultCommand = None
        return resultCommand

    def onAction(self, actionId, actionParams):
        if actionId == BOOTCAMP_BATTLE_ACTION.PLAYER_HIT_VEHICLE:
            assert actionParams
            vehicleId = actionParams[0]
            if vehicleId in self.__enemies:
                self.__shootedEnemy = True
                angle = self.getPlayerHitVehicleAngleCos(vehicleId)
                if angle is not None:
                    if angle >= 0:
                        LOG_DEBUG_DEV_BOOTCAMP('BACK SHOOT')
        return

    def getPlayerHitVehicleAngleCos(self, vehicleId):
        for vehicle in self._avatar.vehicles:
            if vehicle.id != vehicleId:
                continue
            targetVehPosition = vehicle.position
            targetVehDir = Math.Vector3(math.sin(vehicle.yaw), 0.0, math.cos(vehicle.yaw))
            entityDir = targetVehPosition - self._avatar.position
            entityDir.y = 0.0
            entityDir.normalise()
            entityCos = targetVehDir.dot(entityDir)
            return entityCos

        return None

    def __onVehicleKilled(self, targetID, attackerID, *args):
        if targetID in self.__enemies:
            self.__vehicleWasKilled = True

    def onTriggerActivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE and args['vehicleId'] in self.__enemies:
            self.__lockTarget = True

    def onTriggerDeactivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE:
            self.__lockTarget = False


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
