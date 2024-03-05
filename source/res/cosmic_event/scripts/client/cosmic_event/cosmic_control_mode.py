# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/cosmic_control_mode.py
import Math
import Keys
import CommandMapping
from AvatarInputHandler.DynamicCameras import ArcadeCamera
from aih_constants import CTRL_MODE_NAME
from AvatarInputHandler.MapCaseMode import _ArenaBoundsAreaStrikeSelector, MapCaseControlModeBase
from AvatarInputHandler.control_modes import ArcadeControlMode
from AvatarInputHandler import AimingSystems
from cosmic_camera import CosmicCamera
from cosmic_sound import CosmicBattleSounds
TOP_TERRAIN_HEIGHT = 65
BOT_Y = 0
MIN_Y_HEIGHT = 28.0

def rescanPosition(position):
    top = Math.Vector3(position.x, TOP_TERRAIN_HEIGHT, position.z)
    bot = Math.Vector3(position.x, BOT_Y, position.z)
    terrainPos = AimingSystems.__collideStaticOnly(top, bot)
    if terrainPos is not None:
        pos = terrainPos[0]
        pos.y = max(MIN_Y_HEIGHT, pos.y)
        return pos
    else:
        return


class _CosmicArenaBoundStrikeSelector(_ArenaBoundsAreaStrikeSelector):

    def __init__(self, *args, **kwargs):
        super(_CosmicArenaBoundStrikeSelector, self).__init__(*args, **kwargs)
        self.area.enableWaterCollision(True)
        self.area.setMaxHeight(TOP_TERRAIN_HEIGHT)

    def processSelection(self, position, reset=False):
        CosmicBattleSounds.Abilities.blackHoleActivated(reset)
        position = rescanPosition(position)
        return super(_CosmicArenaBoundStrikeSelector, self).processSelection(position, reset) if position is not None else False


class CosmicControlMode(ArcadeControlMode):

    def _setupCamera(self, dataSection):
        self._cam = CosmicCamera(dataSection['camera'], defaultOffset=self._defaultOffset)


class BlackHoleArcadeMapCaseControlMode(MapCaseControlModeBase):
    MODE_NAME = CTRL_MODE_NAME.MAP_CASE_ARCADE

    def _createCamera(self, config, offset=Math.Vector2(0, 0)):
        return ArcadeCamera.ArcadeCamera(config, offset)

    def _initCamera(self):
        self.camera.create()

    def _getCameraDesiredShotPoint(self):
        return self.camera.aimingSystem.getDesiredShotPoint()

    def _getPreferedPositionOnQuit(self):
        return self.camera.aimingSystem.getThirdPersonShotPoint()

    def handleKeyEvent(self, isDown, key, mods, event=None):
        isDeactivateButtonPressed = key == Keys.KEY_ESCAPE or CommandMapping.g_instance.isFired(CommandMapping.CMD_AMMO_CHOICE_3, key)
        super(BlackHoleArcadeMapCaseControlMode, self).handleKeyEvent(isDown, key, mods, event)
        if isDeactivateButtonPressed and mods != Keys.MODIFIER_CTRL and isDown:
            CosmicBattleSounds.Abilities.blackHoleActivated(True)
