# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/hints/HintsScenario.py
import time
import math
from functools import partial
import BattleReplay
import BigWorld
import Math
import TriggersManager
from bootcamp_shared import BOOTCAMP_BATTLE_ACTION
from bootcamp.BootcampConstants import CONSUMABLE_ERROR_MESSAGES, HINT_TYPE
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from debug_utils import LOG_ERROR
from HintsBase import HintBase, HINT_COMMAND
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from bootcamp.Bootcamp import g_bootcamp

class HintAvoidAndDestroy(HintBase, TriggersManager.ITriggerListener):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, avatar, params):
        super(HintAvoidAndDestroy, self).__init__(avatar, HINT_TYPE.HINT_MESSAGE_AVOID, 0)
        self.__detectedEnemy = False
        names = params.get('names', [])
        allVehicles = avatar.arena.vehicles.iteritems()
        self.__vehicleIds = [ vehId for vehId, vehInfo in allVehicles if vehInfo['name'] in names ]
        self.__enemyWasKilled = False
        self.__avatar = avatar
        self.__modelName = self.__getModelName()
        self.__models = []
        self.__active = False

    def start(self):
        self.__active = True
        self._state = HintBase.STATE_DEFAULT
        self._vehicleKilledTrigger = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.VEHICLE_DESTROYED)
        TriggersManager.g_manager.addListener(self)
        self.settingsCore.onSettingsChanged += self.onSettingsChanged

    def stop(self):
        self.__active = False
        self._state = HintBase.STATE_INACTIVE
        self.detachModels()
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delTrigger(self._vehicleKilledTrigger)
            TriggersManager.g_manager.delListener(self)
        self.settingsCore.onSettingsChanged -= self.onSettingsChanged
        return

    def __onModelLoaded(self, attachNode, scaleMatrix, translationMatrix, resourceRefs):
        if self.__modelName not in resourceRefs.failedIDs:
            model = resourceRefs[self.__modelName]
            if not self.__active:
                return
            if attachNode.isDangling or not self.__attaching:
                return
            BigWorld.player().addModel(model)
            yawOnly = Math.WGYawOnlyTransform()
            yawOnly.source = attachNode
            posOnly = Math.WGTranslationOnlyMP()
            posOnly.source = attachNode
            noPithRollMatrix = Math.WGCombinedMP()
            noPithRollMatrix.rotationSrc = yawOnly
            noPithRollMatrix.translationSrc = posOnly
            localTransform = Math.MatrixProduct()
            localTransform.a = scaleMatrix
            localTransform.b = translationMatrix
            refinedMatrixProvider = Math.MatrixProduct()
            refinedMatrixProvider.a = localTransform
            refinedMatrixProvider.b = noPithRollMatrix
            servo = BigWorld.Servo(refinedMatrixProvider)
            model.addMotor(servo)
            self.__models.append({'model': model,
             'servo': servo})
        else:
            LOG_ERROR('Could not load model %s' % self.__modelName)

    def update(self):
        resultCommand = None
        if self._state == HintBase.STATE_DEFAULT:
            if self.__detectedEnemy and not self.__enemyWasKilled:
                self._timeStart = time.time()
                self._state = HintBase.STATE_HINT
                resultCommand = HINT_COMMAND.SHOW
                self.attachModels()
        elif self._state == HintBase.STATE_HINT:
            if self.__enemyWasKilled:
                self._state = HintBase.STATE_INACTIVE
                resultCommand = HINT_COMMAND.HIDE
                self.detachModels()
            elif not self.__detectedEnemy:
                self._state = HintBase.STATE_DEFAULT
                resultCommand = HINT_COMMAND.HIDE
                self.detachModels()
        if BattleReplay.g_replayCtrl.isPlaying:
            resultCommand = None
        return resultCommand

    def onSettingsChanged(self, diff):
        if 'isColorBlind' in diff:
            self.__resetModel()

    def __getModelName(self):
        modPath = 'content/Interface/CheckPoint/'
        modName = 'angle_marker_purple.model' if self.settingsCore.getSetting('isColorBlind') else 'angle_marker.model'
        return modPath + modName

    def __resetModel(self):
        self.__modelName = self.__getModelName()
        self._state = HintBase.STATE_DEFAULT
        self.detachModels()

    def attachModels(self):
        from vehicle_systems.tankStructure import TankPartNames
        self.__attaching = True
        scale = Math.Vector3(4.0, 10.0, 10.0)
        offset = Math.Vector3(0.0, -6.5, 0.0)
        scaleMatrix = Math.Matrix()
        scaleMatrix.setScale(scale)
        translationMatrix = Math.Matrix()
        translationMatrix.setTranslate(offset)
        for vehicle in self.__avatar.vehicles:
            if vehicle.id not in self.__vehicleIds:
                continue
            if vehicle.model is None:
                continue
            attachNode = vehicle.model.node(TankPartNames.TURRET)
            BigWorld.loadResourceListBG((self.__modelName,), partial(self.__onModelLoaded, attachNode, scaleMatrix, translationMatrix))

        return

    def detachModels(self):
        self.__attaching = False
        for data in self.__models:
            data['model'].delMotor(data['servo'])
            BigWorld.player().delModel(data['model'])

        self.__models = []

    def onTriggerActivated(self, args):
        triggerType = args['type']
        if triggerType == TriggersManager.TRIGGER_TYPE.VEHICLE_DESTROYED:
            if args['vehicleId'] in self.__vehicleIds:
                self.__enemyWasKilled = True
                self.detachModels()
        elif triggerType == TriggersManager.TRIGGER_TYPE.VEHICLE_VISUAL_VISIBILITY_CHANGED:
            isVisible = args['isVisible']
            targetId = args['vehicleId']
            if targetId in self.__vehicleIds:
                self.__detectedEnemy = isVisible

    def onTriggerDeactivated(self, args):
        pass


class HintAllyShoot(HintBase):

    def __init__(self, avatar, params):
        super(HintAllyShoot, self).__init__(avatar, HINT_TYPE.HINT_SHOOT_ALLY, params['timeout'])
        self.__alliesIds = [ vehId for vehId, vehInfo in self._avatar.arena.vehicles.items() if vehInfo['team'] == avatar.team ]
        self.__allyShooted = False

    def start(self):
        self._state = HintBase.STATE_DEFAULT

    def stop(self):
        self._state = HintBase.STATE_INACTIVE

    def update(self):
        command = None
        if self._state == HintBase.STATE_DEFAULT:
            if self.__allyShooted:
                self._state = HintBase.STATE_HINT
                command = HINT_COMMAND.SHOW
                self._timeStart = time.time()
                self.__allyShooted = False
        elif self._state == HintBase.STATE_HINT:
            if time.time() - self._timeStart > self._timeout:
                self._state = HintBase.STATE_DEFAULT
                command = HINT_COMMAND.HIDE
        return command

    def onAction(self, actionId, actionParams):
        if actionId != BOOTCAMP_BATTLE_ACTION.PLAYER_HIT_VEHICLE:
            return
        if self._state != HintBase.STATE_DEFAULT:
            return
        vehicleId = actionParams[0]
        if vehicleId in self.__alliesIds and not self.__allyShooted:
            self.__allyShooted = True


class HintUselessConsumable(HintBase):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, avatar, params):
        super(HintUselessConsumable, self).__init__(avatar, HINT_TYPE.HINT_USELESS_CONSUMABLE, params['timeout'])
        self.__isUselessConsumable = False

    def start(self):
        ctrl = self.sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowVehicleErrorByKey += self.__onShowVehicleErrorByKey
        self._state = HintBase.STATE_DEFAULT
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowVehicleErrorByKey -= self.__onShowVehicleErrorByKey
        self._state = HintBase.STATE_INACTIVE
        return

    def update(self):
        command = None
        if self._state == HintBase.STATE_DEFAULT:
            if self.__isUselessConsumable:
                self._state = HintBase.STATE_HINT
                command = HINT_COMMAND.SHOW
                self._timeStart = time.time()
                self.__isUselessConsumable = False
        elif self._state == HintBase.STATE_HINT:
            if time.time() - self._timeStart > self._timeout:
                self._state = HintBase.STATE_DEFAULT
                command = HINT_COMMAND.HIDE
        return command

    def onAction(self, actionId, actionParams):
        pass

    def __onShowVehicleErrorByKey(self, key, args=None, extra=None):
        if key in CONSUMABLE_ERROR_MESSAGES and self._state == HintBase.STATE_DEFAULT:
            self.__isUselessConsumable = True


class HintEnemyTooStrong(HintBase, TriggersManager.ITriggerListener):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, avatar, timeoutMessage, timeoutBetween, enemyVehNames):
        super(HintEnemyTooStrong, self).__init__(avatar, HINT_TYPE.HINT_MESSAGE_SNEAK, timeoutMessage)
        self.__currentVisibleVehicles = set()
        self.__timeoutBetween = timeoutBetween
        self.__strongEnemyVisible = False
        self.__strongEnemiesId = set([ vehId for vehId, vehInfo in self._avatar.arena.vehicles.items() if vehInfo['name'] in enemyVehNames ])
        self._timeStart = time.time()

    def start(self):
        self._state = HintBase.STATE_DEFAULT
        TriggersManager.g_manager.addListener(self)

    def stop(self):
        self._state = HintBase.STATE_INACTIVE
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delListener(self)
        return

    def update(self):
        command = None
        if self._state == HintBase.STATE_DEFAULT:
            if self.__strongEnemyVisible:
                self._state = HintBase.STATE_HINT
                command = HINT_COMMAND.SHOW
                self._timeStart = time.time()
        elif self._state == HintBase.STATE_HINT:
            if time.time() - self._timeStart > self._timeout:
                command = HINT_COMMAND.HIDE
                self._state = HintBase.STATE_INACTIVE
                self._timeStart = time.time()
        elif self._state == HintBase.STATE_INACTIVE:
            if time.time() - self._timeStart > self.__timeoutBetween:
                self._state = HintBase.STATE_DEFAULT
        return command

    def onTriggerActivated(self, args):
        triggerType = args['type']
        if triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_DETECT_ENEMY:
            isVisible = args['isVisible']
            targetId = args['targetId']
            if isVisible:
                self.__currentVisibleVehicles.add(targetId)
            else:
                self.__currentVisibleVehicles.remove(targetId)
            strongVisEnemies = self.__currentVisibleVehicles & self.__strongEnemiesId
            allVehicles = self._avatar.arena.vehicles.iteritems()
            deadEnemies = set([ vehId for vehId, vehInfo in allVehicles if not vehInfo['isAlive'] ])
            strongVisEnemies -= deadEnemies
            self.__strongEnemyVisible = bool(strongVisEnemies)

    def onTriggerDeactivated(self, args):
        pass


class HintBaseCaptured(HintBase, TriggersManager.ITriggerListener):
    STATE_DEFAULT = 0
    STATE_HINT_CAPTURE_BASE = 1
    STATE_HINT_CLOSE_CAPTURE_BASE = 2
    STATE_HINT_CAN_RESET_PROGRESS = 3
    STATE_HINT_CLOSE_CAN_RESET_PROGRESS = 4
    STATE_INACTIVE = 5

    def __init__(self, avatar, vehNames, messageReset):
        super(HintBaseCaptured, self).__init__(avatar, HINT_TYPE.HINT_MESSAGE_CAPTURE_THE_BASE, 0)
        self.__baseCaptureStarted = False
        self.__baseCaptureFinished = False
        self.__enemyWasKilled = False
        self.__wasShooted = False
        self.__messageReset = messageReset
        self.__enemyVehicleIds = set([ vehId for vehId, vehInfo in self._avatar.arena.vehicles.items() if vehInfo['name'] in vehNames ])
        self._timeStart = None
        self._vehicleKilledTrigger = None
        return

    def start(self):
        self._state = HintBaseCaptured.STATE_DEFAULT
        self._avatar.arena.onTeamBasePointsUpdate += self.__onTeamBasePointsUpdate
        self._avatar.arena.onTeamBaseCaptured += self.__onTeamBaseCaptured
        self._vehicleKilledTrigger = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.VEHICLE_DESTROYED)
        TriggersManager.g_manager.addListener(self)

    def stop(self):
        self._state = HintBaseCaptured.STATE_INACTIVE
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delTrigger(self._vehicleKilledTrigger)
            TriggersManager.g_manager.delListener(self)
        return

    def update(self):
        command = None
        if self._state == HintBaseCaptured.STATE_DEFAULT:
            if self.__baseCaptureStarted:
                command = HINT_COMMAND.SHOW
                self._state = HintBaseCaptured.STATE_HINT_CAPTURE_BASE
        elif self._state == HintBaseCaptured.STATE_HINT_CAPTURE_BASE:
            if self.__baseCaptureFinished:
                command = HINT_COMMAND.HIDE
                self._state = HintBaseCaptured.STATE_INACTIVE
            elif self.__wasShooted:
                command = HINT_COMMAND.HIDE
                self._state = HintBaseCaptured.STATE_HINT_CLOSE_CAPTURE_BASE
                self.__wasShooted = False
        elif self._state == HintBaseCaptured.STATE_HINT_CLOSE_CAPTURE_BASE:
            self._state = HintBaseCaptured.STATE_HINT_CAN_RESET_PROGRESS
            self.id = HINT_TYPE.HINT_MESSAGE_RESET_PROGRESS
            command = HINT_COMMAND.SHOW
        elif self._state == HintBaseCaptured.STATE_HINT_CAN_RESET_PROGRESS:
            if self.__enemyWasKilled:
                command = HINT_COMMAND.HIDE
                self._state = HintBaseCaptured.STATE_HINT_CLOSE_CAN_RESET_PROGRESS
        elif self._state == HintBaseCaptured.STATE_HINT_CLOSE_CAN_RESET_PROGRESS:
            self.id = HINT_TYPE.HINT_MESSAGE_CAPTURE_THE_BASE
            command = HINT_COMMAND.SHOW
            self._state = HintBaseCaptured.STATE_HINT_CAPTURE_BASE
        return command

    def __onTeamBasePointsUpdate(self, team, baseID, points, timeLeft, invadersCnt, capturingStopped):
        if team != self._avatar.team and not self.__baseCaptureStarted and points > 0:
            LOG_DEBUG_DEV_BOOTCAMP('__onTeamBasePointsUpdate', team, baseID, timeLeft, invadersCnt, capturingStopped)
            self.__baseCaptureStarted = True

    def __onTeamBaseCaptured(self, team, baseId):
        if team != self._avatar.team:
            self.__baseCaptureFinished = True

    def onTriggerActivated(self, args):
        triggerType = args['type']
        if triggerType == TriggersManager.TRIGGER_TYPE.VEHICLE_DESTROYED:
            if args['vehicleId'] in self.__enemyVehicleIds:
                self.__enemyWasKilled = True
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_RECEIVE_DAMAGE:
            attackerId = args['attackerId']
            if attackerId in self.__enemyVehicleIds:
                self.__wasShooted = True

    def onTriggerDeactivated(self, args):
        pass


class HintStartNarrative(HintBase):

    def __init__(self, avatar, params):
        super(HintStartNarrative, self).__init__(avatar, HINT_TYPE.HINT_START_NARRATIVE, params['timeout'])
        self.__timeBeforeShown = params['time_before_shown']

    def start(self):
        self._state = HintBase.STATE_DEFAULT
        self.__startTime = time.time()

    def stop(self):
        self._state = HintBase.STATE_INACTIVE

    def update(self):
        if self._state == HintBase.STATE_DEFAULT:
            if time.time() - self.__startTime > self.__timeBeforeShown:
                self.__timeShown = time.time()
                self._state = HintBase.STATE_HINT
                return HINT_COMMAND.SHOW
        elif self._state == HintBase.STATE_HINT:
            if time.time() - self.__timeShown > self._timeout:
                self._state = HintBase.STATE_COMPLETE
                return HINT_COMMAND.HIDE
        return None


class HintExitGameArea(HintBase):

    def __init__(self, avatar, params):
        super(HintExitGameArea, self).__init__(avatar, HINT_TYPE.HINT_EXIT_GAME_AREA, params['timeout'])
        boundingBox = avatar.arena.arenaType.boundingBox
        self.__x_min = boundingBox[0][0]
        self.__x_max = boundingBox[1][0]
        self.__z_min = boundingBox[0][1]
        self.__z_max = boundingBox[1][1]
        self.__criteriaDistance = params.get('distance_to_border', 2.0)
        self.__timeHintAppeared = 0.0

    def start(self):
        self._state = HintBase.STATE_DEFAULT

    def stop(self):
        self._state = HintBase.STATE_INACTIVE

    def __isPlayerNearBorder(self):
        x_pos = self._avatar.position.x
        z_pos = self._avatar.position.z
        return abs(x_pos - self.__x_min) < self.__criteriaDistance or abs(x_pos - self.__x_max) < self.__criteriaDistance or abs(z_pos - self.__z_max) < self.__criteriaDistance or abs(z_pos - self.__z_min) < self.__criteriaDistance

    def update(self):
        if self._state == HintBase.STATE_DEFAULT:
            if self.__isPlayerNearBorder():
                self.__timeHintAppeared = time.time()
                self._state = HintBase.STATE_HINT
                return HINT_COMMAND.SHOW
        elif self._state == HintBase.STATE_HINT:
            if time.time() - self.__timeHintAppeared > self._timeout:
                if not self.__isPlayerNearBorder():
                    self._state = HintBase.STATE_DEFAULT
                    return HINT_COMMAND.HIDE
        return None


class HintSectorClear(HintBase, TriggersManager.ITriggerListener):

    def __init__(self, avatar, params):
        super(HintSectorClear, self).__init__(avatar, HINT_TYPE.HINT_SECTOR_CLEAR, params['timeout'])
        enemyNames = params.get('names', [])
        self.__vehicleIds = [ vehId for vehId, vehInfo in self._avatar.arena.vehicles.items() if vehInfo['name'] in enemyNames ]

    def start(self):
        self._state = HintBase.STATE_DEFAULT
        self._vehicleKilledTrigger = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.VEHICLE_DESTROYED)
        TriggersManager.g_manager.addListener(self)

    def stop(self):
        self._state = HintBase.STATE_INACTIVE
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delTrigger(self._vehicleKilledTrigger)
            TriggersManager.g_manager.delListener(self)
        return

    def onTriggerActivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.VEHICLE_DESTROYED:
            killedId = args['vehicleId']
            if killedId in self.__vehicleIds:
                self.__vehicleIds.remove(killedId)

    def onTriggerDeactivated(self, args):
        pass

    def update(self):
        if self._state == HintBase.STATE_DEFAULT:
            if not self.__vehicleIds:
                self._timeStart = time.time()
                self._state = HintBase.STATE_HINT
                return HINT_COMMAND.SHOW
        elif self._state == HintBase.STATE_HINT:
            if time.time() - self._timeStart > self._timeout:
                self._state = HintBase.STATE_INACTIVE
                return HINT_COMMAND.HIDE
        return None


class HintSniperOnDistance(HintBase, TriggersManager.ITriggerListener):

    def __init__(self, avatar, params):
        super(HintSniperOnDistance, self).__init__(avatar, HINT_TYPE.HINT_SNIPER_ON_DISTANCE, params['timeout'])
        self.__originalText = ''
        self.__exitHintText = params['exitHintText']
        self.__exitHintDelay = params.get('exitHintDelay', 3.0)
        self.__enemyIds = [ vehId for vehId, vehInfo in self._avatar.arena.vehicles.items() if vehInfo['name'] in params.get('names', []) ]
        self.__inSniperMode = False
        self.__shootInTarget = False
        self.__angle = params.get('angle', 15.0) * math.pi / 180.0
        self.__distance = params.get('distance', 100)
        self.__waitingForSnipeExit = False
        self.__waitingForSnipeExitTime = 0
        self.__voiceoverEnter = params['enter_voiceover']
        self.__voiceoverExit = params['exit_voiceover']

    @property
    def voiceover(self):
        return self.__voiceoverExit if self.__waitingForSnipeExit else self.__voiceoverEnter

    def start(self):
        self._state = HintBase.STATE_DEFAULT
        self.__originalText = self.message
        self._sniperModeTrigger = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.SNIPER_MODE)
        self._vehicleKilledTrigger = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.VEHICLE_DESTROYED)
        TriggersManager.g_manager.addListener(self)

    def stop(self):
        self._state = HintBase.STATE_INACTIVE
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delTrigger(self._sniperModeTrigger)
            TriggersManager.g_manager.delTrigger(self._vehicleKilledTrigger)
            TriggersManager.g_manager.delListener(self)
        return

    def onTriggerActivated(self, args):
        triggerType = args['type']
        if triggerType == TriggersManager.TRIGGER_TYPE.SNIPER_MODE:
            self.__inSniperMode = True
        elif triggerType == TriggersManager.TRIGGER_TYPE.VEHICLE_DESTROYED:
            killedId = args['vehicleId']
            if killedId in self.__enemyIds:
                self.__waitingForSnipeExit = self.__inSniperMode
                self.__waitingForSnipeExitTime = time.time()
                self.__enemyIds.remove(killedId)
        elif triggerType == TriggersManager.TRIGGER_TYPE.PLAYER_SHOOT:
            if not self.__inSniperMode:
                _, self.__shotVector = self._avatar.gunRotator.getCurShotPosition()
                self.__shotVector.normalise()
                if self.isDirInShootingAngle(self.__shotVector):
                    self.__shootInTarget = True

    def onTriggerDeactivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.SNIPER_MODE:
            self.__inSniperMode = False
            self.__waitingForSnipeExit = False
            self._timeStart = time.time() - self._timeout

    def update(self):
        if self._state == HintBase.STATE_INACTIVE:
            return None
        else:
            _, shotVector = self._avatar.gunRotator.getCurShotPosition()
            shotVector.normalise()
            inShootingRange = self.isDirInShootingAngle(shotVector)
            if self._state == HintBase.STATE_DEFAULT:
                if self.__waitingForSnipeExit and time.time() - self.__waitingForSnipeExitTime > self.__exitHintDelay:
                    self.message = self.__exitHintText
                    self._state = HintBase.STATE_HINT
                    self._timeStart = time.time()
                    return HINT_COMMAND.SHOW
                if (self.__shootInTarget or inShootingRange) and not self.__inSniperMode:
                    self._state = HintBase.STATE_HINT
                    self._timeStart = time.time()
                    g_bootcamp.resetSniperModeUsed()
                    return HINT_COMMAND.SHOW
            elif self._state == HintBase.STATE_HINT and (self.__inSniperMode and not self.__waitingForSnipeExit or not inShootingRange and not self.__waitingForSnipeExit):
                self._state = HintBase.STATE_DEFAULT
                self.__shootInTarget = False
                self.message = self.__originalText
                return HINT_COMMAND.HIDE
            return None

    def isDirInShootingAngle(self, shootVector):
        for vehicle in self._avatar.vehicles:
            if vehicle.id in self.__enemyIds and vehicle.isAlive():
                position = vehicle.position
                playerPosition = BigWorld.entity(self._avatar.playerVehicleID).position
                direction = position - playerPosition
                direction.normalise()
                cosAlpha = shootVector.dot(direction)
                if cosAlpha > math.cos(self.__angle) and playerPosition.flatDistTo(position) > self.__distance:
                    return True

        return False

    def onAction(self, actionId, actionParams):
        if actionId == BOOTCAMP_BATTLE_ACTION.PLAYER_MOVE:
            flags = actionParams[0]
            if flags > 0 and self.__waitingForSnipeExit:
                self.__waitingForSnipeExitTime = time.time() - self.__exitHintDelay


class HintLowHP(HintBase):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, avatar, params):
        super(HintLowHP, self).__init__(avatar, HINT_TYPE.HINT_LOW_HP, params['timeout'])
        self.__params = params
        self.__avatarHealth = None
        self.__lowHPFirstValue = None
        self.__lowHPSecondValue = None
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vehicle = ctrl.getControllingVehicle()
            if vehicle is not None:
                self.__setHealthValues(vehicle)
            else:
                ctrl.onVehicleControlling += self.__onVehicleControlling
        self.__isFirstWarningAppeared = False
        self.__isSecondWarningAppeared = False
        self.__timeShown = 0.0
        return

    def start(self):
        self._state = HintBase.STATE_DEFAULT

    def stop(self):
        self._state = HintBase.STATE_INACTIVE
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            ctrl.onVehicleControlling -= self.__onVehicleControlling
        return

    def update(self):
        if self.__avatarHealth is None:
            return
        else:
            command = None
            if self._state == HintBase.STATE_DEFAULT:
                showHint = False
                if not self.__isFirstWarningAppeared:
                    if self.__avatarHealth < self.__lowHPFirstValue:
                        self.__isFirstWarningAppeared = True
                        showHint = True
                elif self.__avatarHealth < self.__lowHPSecondValue:
                    self.__isSecondWarningAppeared = True
                    showHint = True
                if showHint:
                    self._state = HintBase.STATE_HINT
                    command = HINT_COMMAND.SHOW
                    self.__timeShown = time.time()
            elif self._state == HintBase.STATE_HINT:
                if time.time() - self.__timeShown > self._timeout:
                    if self.__isSecondWarningAppeared:
                        self._state = HintBase.STATE_INACTIVE
                    else:
                        self._state = HintBase.STATE_DEFAULT
                    return HINT_COMMAND.HIDE
            return command

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.HEALTH:
            self.__avatarHealth = value

    def __onVehicleControlling(self, vehicle):
        if vehicle.isPlayerVehicle:
            self.__setHealthValues(vehicle)

    def __setHealthValues(self, vehicle):
        self.__avatarHealth = vehicle.health
        self.__lowHPFirstValue = self.__params['first_percent'] * self.__avatarHealth
        self.__lowHPSecondValue = self.__params['second_percent'] * self.__avatarHealth
