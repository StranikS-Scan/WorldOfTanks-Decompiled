# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_to_camera_alignment_components.py
import BigWorld
import CGF
import DebugDrawer
import Math
import logging
import math_utils
from WeakMethod import WeakMethodProxy
from CameraComponents import CameraComponent
from constants import IS_CLIENT
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from cgf_script.component_meta_class import registerComponent
from cgf_script.managers_registrator import registerManager, onAddedQuery, registerRule, Rule, tickGroup
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.shared import g_eventBus
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.tankStructure import TankPartIndexes
if IS_CLIENT:
    from AvatarInputHandler.cameras import getViewProjectionMatrix
_logger = logging.getLogger(__name__)
_DEFAULT_SCREEN_TL_CORNER = Math.Vector2(208, 162)
_DEFAULT_SCREEN_BR_CORNER = Math.Vector2(1552, 1194)

class _AlignmentCameraVisuals(object):

    def __init__(self):
        self.enabled = False

    def toggle(self):
        self.enabled ^= True

    def draw(self, aabbCenter, vehicleSize, frameCenter):
        DebugDrawer.DebugDrawer().cube().zTest(False).wireframe(True).colour(4278255360L).position(aabbCenter).scale(vehicleSize)
        DebugDrawer.DebugDrawer().sphere().zTest(False).wireframe(True).colour(4294967040L).position(frameCenter).scale(Math.Vector3(0.2, 0.2, 0.2))
        DebugDrawer.DebugDrawer().line().zTest(False).colour(4294967040L).points([aabbCenter, frameCenter])


g_alignmentCameraVisuals = _AlignmentCameraVisuals()

@registerComponent
class VehicleToCameraAlignmentComponent(object):
    editorTitle = 'Vehicle To Camera Alignment Component'
    serialName = 'VehicleToCameraAlignmentComponent'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor


class VehicleToCameraAlignmentManager(CGF.ComponentManager):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _query = CGF.QueryConfig(CGF.GameObject, VehicleToCameraAlignmentComponent, CameraComponent)

    def __init__(self, *args):
        super(VehicleToCameraAlignmentManager, self).__init__(*args)
        self.__aabbCenter = None
        self.__vehicleSize = None
        self.__shouldAlignCenters = False
        self.__screenWidth, self.__screenHeight = BigWorld.windowSize()
        self.__resizeHandled = False
        self.__screenTopLeftCorner = Math.Vector3(_DEFAULT_SCREEN_TL_CORNER.x, _DEFAULT_SCREEN_TL_CORNER.y, 0.0)
        self.__screenBottomRightCorner = Math.Vector3(_DEFAULT_SCREEN_BR_CORNER.x, _DEFAULT_SCREEN_BR_CORNER.y, 0.0)
        self.__callbackDelayer = CallbackDelayer()
        return

    def activate(self):
        from cgf_components.hangar_camera_manager import HangarCameraManager
        g_eventBus.addListener(CameraRelatedEvents.ON_RESIZE, self.__handleResize)
        cameraManager = CGF.getManager(self._hangarSpace.spaceID, HangarCameraManager)
        if cameraManager:
            cameraManager.onCameraSwitched += self.__onCameraSwitched

    def deactivate(self):
        from cgf_components.hangar_camera_manager import HangarCameraManager
        cameraManager = CGF.getManager(self._hangarSpace.spaceID, HangarCameraManager)
        if cameraManager:
            cameraManager.onCameraSwitched -= self.__onCameraSwitched
        g_eventBus.removeListener(CameraRelatedEvents.ON_RESIZE, self.__handleResize)

    def alignCamera(self, cameraName):
        self.__shouldAlignCenters = False
        for _, _, cameraComponent in self._query:
            if cameraComponent.name == cameraName:
                self.__shouldAlignCenters = True
                self.__callbackDelayer.delayCallback(0.0, WeakMethodProxy(self.__waitAABBLoaded))

    def getTargetPosition(self):
        return self.__aabbCenter

    @onAddedQuery(VehicleToCameraAlignmentComponent)
    def onAdded(self, _):
        _logger.debug('VehicleToCameraAlignmentManager is activated')

    @tickGroup(groupName='Simulation')
    def tick(self):
        if self.__aabbCenter:
            if g_alignmentCameraVisuals.enabled:
                vp = getViewProjectionMatrix()
                pointInWorld = Math.Vector4(self.__aabbCenter.x, self.__aabbCenter.y, self.__aabbCenter.z, 1.0)
                pointInClip = vp.applyV4Point(pointInWorld)
                depth = pointInClip.z / pointInClip.w
                centerInLocal = Math.Vector2((self.__screenBottomRightCorner.x + self.__screenTopLeftCorner.x) * 0.5, (self.__screenBottomRightCorner.y + self.__screenTopLeftCorner.y) * 0.5)
                frameCenter = self.__projectViewportToWorld(centerInLocal, depth)
                g_alignmentCameraVisuals.draw(self.__aabbCenter, self.__vehicleSize, frameCenter)
            if self.__shouldAlignCenters and self.__resizeHandled:
                self.__alignCenters()
            screenWidth, screenHeight = BigWorld.windowSize()
            if self.__screenWidth != screenWidth or self.__screenHeight != screenHeight:
                self.__resizeHandled = False

    def __onCameraSwitched(self, cameraName):
        self.alignCamera(cameraName)

    def __handleResize(self, event):
        ctx = event.ctx
        self.__screenTopLeftCorner.x = ctx['xmin']
        self.__screenTopLeftCorner.y = ctx['ymin']
        self.__screenBottomRightCorner.x = ctx['xmax']
        self.__screenBottomRightCorner.y = ctx['ymax']
        self.__screenWidth, self.__screenHeight = BigWorld.windowSize()
        self.__resizeHandled = True

    def __waitAABBLoaded(self):
        self.__aabbCenter = self.__getHangarVehicleCenter()
        if self.__aabbCenter:
            camera = BigWorld.camera()
            targetMatrix = Math.Matrix()
            targetMatrix.setTranslate(self.__aabbCenter)
            camera.target = targetMatrix
            return None
        else:
            return 0

    def __getHangarVehicleCenter(self):
        if not self._hangarSpace:
            return None
        else:
            appearance = self._hangarSpace.getVehicleEntityAppearance()
            if not appearance or not appearance.collisions:
                return None
            collisions = appearance.collisions
            enclosingAABB = [Math.Vector3(float('inf')), Math.Vector3(-float('inf'))]
            for index in TankPartIndexes.ALL:
                aabb = collisions.getBoundingBox(index)
                partMatrix = Math.Matrix(appearance.compoundModel.node(TankPartIndexes.getName(index)))
                localPoints = [Math.Vector3(aabb[0].x, aabb[0].y, aabb[0].z),
                 Math.Vector3(aabb[0].x, aabb[0].y, aabb[1].z),
                 Math.Vector3(aabb[1].x, aabb[0].y, aabb[0].z),
                 Math.Vector3(aabb[1].x, aabb[0].y, aabb[1].z),
                 Math.Vector3(aabb[0].x, aabb[1].y, aabb[0].z),
                 Math.Vector3(aabb[0].x, aabb[1].y, aabb[1].z),
                 Math.Vector3(aabb[1].x, aabb[1].y, aabb[1].z),
                 Math.Vector3(aabb[1].x, aabb[1].y, aabb[0].z)]
                for localPoint in localPoints:
                    worldCord = partMatrix.applyPoint(localPoint)
                    enclosingAABB[0].x = min(enclosingAABB[0].x, worldCord.x)
                    enclosingAABB[0].y = min(enclosingAABB[0].y, worldCord.y)
                    enclosingAABB[0].z = min(enclosingAABB[0].z, worldCord.z)
                    enclosingAABB[1].x = max(enclosingAABB[1].x, worldCord.x)
                    enclosingAABB[1].y = max(enclosingAABB[1].y, worldCord.y)
                    enclosingAABB[1].z = max(enclosingAABB[1].z, worldCord.z)

            self.__vehicleSize = Math.Vector3(enclosingAABB[1].x - enclosingAABB[0].x, enclosingAABB[1].y - enclosingAABB[0].y, enclosingAABB[1].z - enclosingAABB[0].z)
            position = math_utils.getCenterFromBox(enclosingAABB)
            return position

    def __projectViewportToWorld(self, viewportPoint, depth):
        screenWidth, screenHeight = BigWorld.windowSize()
        ndcP = Math.Vector3(2.0 * viewportPoint.x / screenWidth - 1, 1 - 2.0 * viewportPoint.y / screenHeight, depth)
        ndcP = Math.Vector4(ndcP.x, ndcP.y, ndcP.z, 1.0)
        invVP = getViewProjectionMatrix()
        invVP.invert()
        pointInWorld = invVP.applyV4Point(ndcP)
        pointInWorld = Math.Vector3(pointInWorld.x / pointInWorld.w, pointInWorld.y / pointInWorld.w, pointInWorld.z / pointInWorld.w)
        return pointInWorld

    def __alignCenters(self):
        camera = BigWorld.camera()
        screenWidth, screenHeight = BigWorld.windowSize()
        vp = getViewProjectionMatrix()
        clipPos = vp.applyV4Point(Math.Vector4(self.__aabbCenter.x, self.__aabbCenter.y, self.__aabbCenter.z, 1.0))
        depth = clipPos.z / clipPos.w
        centerPointInScreen = Math.Vector2(screenWidth * 0.5, screenHeight * 0.5)
        visiblePointInScreen = Math.Vector2((self.__screenBottomRightCorner.x + self.__screenTopLeftCorner.x) * 0.5, (self.__screenBottomRightCorner.y + self.__screenTopLeftCorner.y) * 0.5)
        centerPointInWorld = self.__projectViewportToWorld(centerPointInScreen, depth)
        visiblePointInWorld = self.__projectViewportToWorld(visiblePointInScreen, depth)
        localFromWS = Math.Matrix()
        localFromWS.setRotateYPR((camera.currentYPR.x, camera.currentYPR.z, 0.0))
        localFromWS.invert()
        screenCenterInLocal = localFromWS.applyPoint(centerPointInWorld)
        visiblePointInLocal = localFromWS.applyPoint(visiblePointInWorld)
        pivotPosition = screenCenterInLocal - visiblePointInLocal
        camera.pivotPosition = pivotPosition


@registerRule
class VehicleToCameraAlignmentRule(Rule):
    category = 'Hangar rules'
    domain = CGF.DomainOption.DomainClient

    @registerManager(VehicleToCameraAlignmentManager)
    def reg1(self):
        return None
