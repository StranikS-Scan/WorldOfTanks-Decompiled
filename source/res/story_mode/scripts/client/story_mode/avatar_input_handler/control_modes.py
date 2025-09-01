# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/avatar_input_handler/control_modes.py
import math
import typing
import BigWorld
import CommandMapping
import GUI
import Keys
import Math
import SoundGroups
import math_utils
from AvatarInputHandler import aih_global_binding
from AvatarInputHandler.DynamicCameras.ArcadeCamera import ArcadeCamera
from AvatarInputHandler.DynamicCameras.StrategicCamera import StrategicCamera
from AvatarInputHandler.MapCaseMode import AracdeMinefieldControleMode, MapCaseControlMode
from AvatarInputHandler.control_modes import IControlMode, ArcadeControlMode, SniperControlMode
from Vehicle import Vehicle
from account_helpers.settings_core import settings_constants
from aih_constants import CTRL_MODE_NAME
from constants import AIMING_MODE, VEHICLE_BUNKER_TURRET_TAG
from helpers import dependency
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from story_mode.gui.app_loader import observers
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode_common.story_mode_constants import RECON_ABILITY, EQUIPMENT_STAGES as STAGES
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
    from story_mode_common.items.sm_artefacts import BaseAbilityEquipment

def targetIsBunker():
    target = BigWorld.target()
    return False if not isinstance(target, Vehicle) else VEHICLE_BUNKER_TURRET_TAG in target.typeDescriptor.type.tags


class StoryModeArcadeCamera(ArcadeCamera):
    _START_DISTANCE = 10
    _START_ANGLE = 80

    def create(self, onChangeControlMode=None, postmortemMode=False, smartPointCalculator=True):
        prevStartDist = self._cfg['startDist']
        prevStartAngle = self._cfg['startAngle']
        self._cfg['startDist'] = self._START_DISTANCE
        self._cfg['startAngle'] = math.radians(self._START_ANGLE) - math.pi * 0.5
        super(StoryModeArcadeCamera, self).create(onChangeControlMode, postmortemMode, smartPointCalculator)
        self._cfg['startDist'] = prevStartDist
        self._cfg['startAngle'] = prevStartAngle


class StoryModeArcadeControlModeStartCamera(ArcadeControlMode):

    def _setupCamera(self, dataSection):
        self._cam = StoryModeArcadeCamera(dataSection['camera'], defaultOffset=self._defaultOffset)


class LockTargetDisabler(IControlMode):

    def handleKeyEvent(self, isDown, key, mods, event=None):
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_CM_LOCK_TARGET, key) and self._isLockTargetDisabled():
            if cmdMap.isFired(CommandMapping.CMD_CM_FREE_CAMERA, key):
                self.setAimingMode(isDown, AIMING_MODE.USER_DISABLED)
            return False
        return super(LockTargetDisabler, self).handleKeyEvent(isDown, key, mods, event)

    def _isLockTargetDisabled(self):
        return True


class OnboardingArcadeControlMode(LockTargetDisabler, StoryModeArcadeControlModeStartCamera):
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    @property
    def isWinMessageShown(self):
        battlePage = observers.getStoryModeBattle()
        return battlePage is not None and battlePage.isWinMessageShown

    def handleKeyEvent(self, isDown, key, mods, event=None):
        return False if CommandMapping.g_instance.isFired(CommandMapping.CMD_CM_ALTERNATE_MODE, key) and self.isWinMessageShown else super(OnboardingArcadeControlMode, self).handleKeyEvent(isDown, key, mods, event)

    def onChangeControlModeByScroll(self):
        if self.isWinMessageShown:
            return
        super(OnboardingArcadeControlMode, self).onChangeControlModeByScroll()

    def _isLockTargetDisabled(self):
        return self._storyModeCtrl.isOnboarding


class OnboardingSniperControlMode(LockTargetDisabler, SniperControlMode):
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def _isLockTargetDisabled(self):
        return self._storyModeCtrl.isOnboarding


class StoryModeArcadeControlMode(LockTargetDisabler, StoryModeArcadeControlModeStartCamera):

    def _isLockTargetDisabled(self):
        return targetIsBunker()


class StoryModeSniperControlMode(LockTargetDisabler, SniperControlMode):

    def _isLockTargetDisabled(self):
        return targetIsBunker()


class StoryModeArcadeMinefieldControlMode(AracdeMinefieldControleMode):
    pass


class SMStrategicCamera(StrategicCamera):
    _TICK_TIME = 0.01

    def __init__(self, dataSec):
        super(SMStrategicCamera, self).__init__(dataSec)
        self.minApplyRadius = 0.0
        self.maxApplyRadius = 0.0
        self._lastPosition = None
        self._tickID = None
        return

    def update(self, dx, dy, dz, rotateMode=True, zoomMode=True, updatedByKeyboard=False):
        if self.maxApplyRadius > 0 or self.minApplyRadius > 0:
            vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
            playerPosition = vehicle.position
            altModeEnabled = self.settingsCore.getSetting(settings_constants.SPGAim.SPG_STRATEGIC_CAM_MODE) == 1
            if altModeEnabled:
                shotPoint = self.aimingSystem.getDesiredShotPoint()
                prevDistance = playerPosition.distTo(shotPoint)
                newDistance = prevDistance - dy * self.getCurSense()
                if self.minApplyRadius > 0 and newDistance < self.minApplyRadius and dy > 0:
                    dy *= (prevDistance - self.minApplyRadius) / (prevDistance - newDistance)
                if self.maxApplyRadius > 0 and newDistance > self.maxApplyRadius and dy < 0:
                    dy *= (self.maxApplyRadius - prevDistance) / (newDistance - prevDistance)
            else:
                delta = Math.Vector3(float(dx), 0, float(-dy)) * self.getCurSense()
                prevCameraPos = self.aimingSystem.planePosition
                position = Math.Vector3(prevCameraPos.x, playerPosition.y, prevCameraPos.z)
                newPoint = position + delta
                distance = playerPosition.distTo(newPoint)
                isMinDistance = self.minApplyRadius > 0 and distance < self.minApplyRadius
                isMaxDistance = self.maxApplyRadius > 0 and distance > self.maxApplyRadius
                if isMinDistance or isMaxDistance:
                    k = (self.minApplyRadius if isMinDistance else self.maxApplyRadius) / distance
                    newPointDelta = Math.Vector3((newPoint.x - playerPosition.x) * k, 0, (newPoint.z - playerPosition.z) * k)
                    newPoint = playerPosition + newPointDelta
                    dx = (newPoint.x - prevCameraPos.x) / self.getCurSense()
                    dy = -(newPoint.z - prevCameraPos.z) / self.getCurSense()
        super(SMStrategicCamera, self).update(dx, dy, dz, rotateMode, zoomMode, updatedByKeyboard)

    def enable(self, targetPos, saveDist, switchToPos=None, switchToPlace=None):
        playerPosition = self._getPlayerPosition()
        if self.maxApplyRadius > 0:
            distance = playerPosition.distTo(targetPos)
            if distance > self.maxApplyRadius:
                targetPos = Math.Vector3(playerPosition + Math.Vector3(targetPos - playerPosition).scale(self.maxApplyRadius / distance))
        super(SMStrategicCamera, self).enable(targetPos, saveDist, switchToPos, switchToPlace)
        self._lastPosition = Math.Vector3(playerPosition)
        self._tickID = BigWorld.callback(self._TICK_TIME, self._tick)

    def disable(self):
        if self._tickID is not None:
            BigWorld.cancelCallback(self._tickID)
            self._tickID = None
        super(SMStrategicCamera, self).disable()
        return

    @staticmethod
    def _getConfigsKey():
        return SMStrategicCamera.__name__

    @staticmethod
    def _getPlayerPosition():
        vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        return vehicle.position

    def _tick(self):
        position = self._getPlayerPosition()
        lastPosition = self._lastPosition
        if lastPosition.x != position.x or lastPosition.y != position.y or lastPosition.z != position.z:
            self.update(position.x - lastPosition.x, position.z - lastPosition.z, position.y - lastPosition.y)
            lastPosition.x = position.x
            lastPosition.y = position.y
            lastPosition.z = position.z
        self._tickID = BigWorld.callback(self._TICK_TIME, self._tick)


class SMStrategicMapCaseControlMode(MapCaseControlMode):
    MODE_NAME = CTRL_MODE_NAME.SM_STRATEGIC

    def enable(self, **args):
        equipmentID = args.get('equipmentID', None)
        if equipmentID is not None:
            equipment = vehicles.g_cache.equipments()[equipmentID]
            self.camera.minApplyRadius = equipment.minApplyRadius
            self.camera.maxApplyRadius = equipment.maxApplyRadius
        super(SMStrategicMapCaseControlMode, self).enable(**args)
        return

    def _createCamera(self, config, offset=Math.Vector2(0, 0)):
        self._acceptsArcadeState = False
        return SMStrategicCamera(config)


class SMEntityViewMode(IControlMode):
    _guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    _aimOffset = aih_global_binding.bindRO(aih_global_binding.BINDING_ID.AIM_OFFSET)
    _MOVE_CMDS = (CommandMapping.CMD_MOVE_FORWARD,
     CommandMapping.CMD_MOVE_FORWARD_SPEC,
     CommandMapping.CMD_MOVE_BACKWARD,
     CommandMapping.CMD_ROTATE_LEFT,
     CommandMapping.CMD_ROTATE_RIGHT,
     CommandMapping.CMD_INCREMENT_CRUISE_MODE,
     CommandMapping.CMD_DECREMENT_CRUISE_MODE)

    def __init__(self, dataSection, _):
        self._cam = ArcadeCamera(dataSection['camera'], dataSection.readVector2('defaultOffset'))
        self._entityID = None
        self._isEnabled = False
        return

    @property
    def curVehicleID(self):
        return self._entityID

    @property
    def camera(self):
        return self._cam

    def isSelfVehicle(self):
        return False

    def isEnabled(self):
        return self._isEnabled

    def create(self):
        self._cam.create(onChangeControlMode=None, postmortemMode=True, smartPointCalculator=False)
        return

    def destroy(self):
        self.disable()
        self._cam.destroy()
        self._cam = None
        return

    def enable(self, **args):
        BigWorld.player().autoAim(None)
        SoundGroups.g_instance.changePlayMode(0)
        entityId = args.get('entityId', None)
        if entityId is not None:
            self._entityID = entityId
            entity = BigWorld.entities.get(entityId)
            if entity is not None:
                self._cam.enable()
                self._cam.vehicleMProv = entity.matrix
                self._isEnabled = True
        return

    def disable(self):
        self._cam.disable()
        self._isEnabled = False

    def handleMouseEvent(self, dx, dy, dz):
        GUI.mcursor().position = self._aimOffset
        self._cam.update(dx, dy, math_utils.clamp(-1, 1, dz))
        return True

    def handleKeyEvent(self, isDown, key, mods, event=None):
        reconItem = self._guiSessionProvider.shared.equipments.getEquipmentByName(RECON_ABILITY)
        if reconItem is not None:
            stage = reconItem.getStage()
            if stage in (STAGES.ACTIVATING, STAGES.ACTIVE, STAGES.DEACTIVATING):
                args = {'name': reconItem.getDescriptor().userString}
                if CommandMapping.g_instance.isActiveList(self._MOVE_CMDS):
                    self._showMessage('ability_unable_to_move', args)
                    return False
                if CommandMapping.g_instance.isActive(CommandMapping.CMD_CM_SHOOT):
                    self._showMessage('ability_unable_to_fire', args)
                    return False
            if stage == STAGES.ACTIVE and BigWorld.isKeyDown(Keys.KEY_RIGHTMOUSE):
                battlePage = observers.getStoryModeBattle()
                if battlePage is not None and not battlePage.isFullMapVisible:
                    self._guiSessionProvider.shared.equipments.cancel()
                    return True
        return False

    def _showMessage(self, msgName, args):
        self._guiSessionProvider.shared.messages.showVehicleError(msgName, args)
