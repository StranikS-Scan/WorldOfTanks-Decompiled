# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/avatar_input_handler/grinch_map_case_mode.py
import Math
import BigWorld
from aih_constants import CTRL_MODE_NAME
from AvatarInputHandler import MapCaseMode
from AvatarInputHandler.DynamicCameras import ArcadeCamera
from constants import CollisionFlags
from grinch_common.grinch_constants import TURRET_SPHERE_COLLIDER_RADIUS

class GrinchStrikeSelector(MapCaseMode._ArcadeBomberStrikeSelector):

    def __init__(self, position, equipment):
        super(GrinchStrikeSelector, self).__init__(position, equipment)
        self.area.enableAccurateCollision(False)
        self.outFromBoundsAimArea.enableAccurateCollision(False)


class GrinchTurretStrikeSelector(MapCaseMode._ArenaBoundsAreaStrikeSelector):

    def __init__(self, position, equipment):
        self.ctrlMode = BigWorld.player().inputHandler.ctrls.get(CTRL_MODE_NAME.MAP_CASE_ARCADE, None)
        super(GrinchTurretStrikeSelector, self).__init__(position, equipment, terrainOnly=True)
        self.area.enableAccurateCollision(False)
        self.outFromBoundsAimArea.enableAccurateCollision(False)
        return

    def _isTerrain(self, position):
        spaceId = BigWorld.player().spaceID
        terrainChecker = BigWorld.wg_collideCustomSphereDynamicStatic(spaceId, position + Math.Vector3(0, 12, 0), position + Math.Vector3(0, TURRET_SPHERE_COLLIDER_RADIUS, 0), self.ctrlMode.turretSphereCollider, CollisionFlags.TRIANGLE_TERRAIN)
        return not terrainChecker


class GrinchArcadeMapCaseControlMode(MapCaseMode.MapCaseControlModeBase):
    MODE_NAME = CTRL_MODE_NAME.MAP_CASE_ARCADE

    def __init__(self, dataSection, avatarInputHandler):
        self.turretSphereCollider = None
        super(GrinchArcadeMapCaseControlMode, self).__init__(dataSection, avatarInputHandler)
        return

    def destroy(self):
        if self.turretSphereCollider is not None:
            BigWorld.wg_destroyCollideShape(BigWorld.player().spaceID, self.turretSphereCollider)
        super(GrinchArcadeMapCaseControlMode, self).destroy()
        return

    def _createCamera(self, config, offset=Math.Vector2(0, 0)):
        return ArcadeCamera.ArcadeCamera(config, offset)

    def _initCamera(self):
        self.camera.create()
        self.turretSphereCollider = BigWorld.wg_createCollideSphere(BigWorld.player().spaceID, TURRET_SPHERE_COLLIDER_RADIUS)

    def _getCameraDesiredShotPoint(self):
        position = self.camera.aimingSystem.getDesiredShotPoint()
        terrainCollide = BigWorld.wg_collideSegment(BigWorld.player().spaceID, position + Math.Vector3(0, 1000, 0), position + Math.Vector3(0, -1000, 0), 128, 8)
        return terrainCollide.closestPoint if terrainCollide else position

    def _getPreferedPositionOnQuit(self):
        return self.camera.aimingSystem.getThirdPersonShotPoint()
