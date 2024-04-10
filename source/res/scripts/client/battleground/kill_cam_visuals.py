# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/kill_cam_visuals.py
import math
import logging
import BigWorld
import CGF
import GenericComponents
import Math
import math_utils
from cgf_components.highlight_component import HighlightComponent
from cgf_components.visual_effect_component_manager import ImpactZoneComponent
from dyn_objects_cache import _KillCamEffectDynObjects
from functools import partial
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
_BOUND_MODELS_IMPACT_OFFSET = 0.025
_UNSPOTTED_CONE_RANDOM_OFFSET = 5
_UNSPOTTED_CONE_MAX_PITCH = 1077
LINE_WIDTH = 3
_logger = logging.getLogger(__name__)
_LENGTH_FACTOR = 2.08
_DOTS_SPACING = 0.06

class EffectsController(CallbackDelayer):

    def __init__(self):
        super(EffectsController, self).__init__()
        self.gameObjects = []
        dynObjectsCache = dependency.instance(IBattleDynamicObjectsCache)
        self.__effectsPathsConfig = dynObjectsCache.getFeaturesConfig(_KillCamEffectDynObjects.CONFIG_NAME)

    def destroy(self):
        _logger.info('[EffectsController] Destroy Kill Cam Effects')
        self.hideEdges()
        self.delayCallback(0.0, self.__removeGameObjects)

    def hideEdges(self):
        self.__removeEdgeDrawer()

    def displayKillCamEffects(self, vehicleAppearance, maxComponentIndex, hasProjectilePierced, isSPG, isSpotted, isShellHE, explosionRadius, trajectoryPoints, segments, impactPoint, isRicochet):
        _logger.info('displayKillCamEffects (params): %s %s %s %s %s %s %s %s %s %s', vehicleAppearance, maxComponentIndex, hasProjectilePierced, isSPG, isSpotted, isShellHE, explosionRadius, trajectoryPoints, segments, impactPoint)
        if trajectoryPoints[-1] != impactPoint:
            self.__spawnSpacedArmorLine(trajectoryPoints[-1], impactPoint)
            self.__spawnSpacedArmorImpactPoint(trajectoryPoints[-1])
        if not hasProjectilePierced and not isShellHE:
            _logger.error('Unexpected shell data.')
            return False
        if not hasProjectilePierced:
            if isSPG:
                self.__spawnExplosionSphere(trajectoryPoints[-1], explosionRadius)
            else:
                self.__spawnImpactZone(segments, vehicleAppearance, maxComponentIndex)
        if isSpotted and (isSPG or hasProjectilePierced):
            self.__spawnShellTrajectory(trajectoryPoints, isSPG, isRicochet)
            self.__spawnImpactPoint(impactPoint)
        elif isSpotted:
            self.__spawnShellTrajectory(trajectoryPoints, isSPG, isRicochet)
        else:
            self.__spawnHitCone(trajectoryPoints[0], trajectoryPoints[-1])

    def __removeEdgeDrawer(self):
        for go in self.gameObjects:
            highlightComponent = go.findComponentByType(HighlightComponent)
            if highlightComponent:
                go.removeComponentByType(HighlightComponent)

    def __removeGameObjects(self):
        for go in self.gameObjects:
            _logger.info('[EffectsController] Remove - %s', go)
            CGF.removeGameObject(go)

        self.gameObjects = []

    def __spawnHitCone(self, hitPosition, originPosition):

        def cbHitCone(go):
            direction = Math.Vector3(hitPosition - originPosition)
            rotation = Math.Vector3(direction.yaw, direction.pitch, 0)
            maximumPitch = math.radians(_UNSPOTTED_CONE_MAX_PITCH)
            pitch = math_utils.clamp(-maximumPitch, 0, rotation.y)
            rotation = Math.Vector3(rotation.x, pitch, rotation.z)
            self.__setTransformToGameObject(go, (1, 1, 1), rotation, originPosition)
            self.gameObjects.append(go)

        CGF.loadGameObject(self.__effectsPathsConfig.cone, BigWorld.player().spaceID, Math.Vector3(0, 0, 0), cbHitCone)

    def __spawnShellTrajectory(self, points, isSpgShot=False, isRicochet=False):

        def cbEmptyTrajectory(go):

            def cbTrajectoryModel(scale, rotation, position, go):
                self.__setTransformToGameObject(go, scale, rotation, position)
                self.gameObjects.append(go)

            if not isSpgShot and not isRicochet:
                lastPoint = points[-1]
                prevPoint = points[0]
                gradientPoint = (prevPoint - lastPoint) * 0.1 + lastPoint
                points.insert(-1, gradientPoint)
            ptsLen = len(points)
            for i in range(ptsLen - 1):
                direction = Math.Vector3(points[i + 1] - points[i])
                translation = points[i]
                scale = (LINE_WIDTH, LINE_WIDTH, direction.length / _LENGTH_FACTOR)
                rotation = Math.Vector3(direction.yaw, direction.pitch, 0)
                modelPath = self.__effectsPathsConfig.trajectoryGradient if ptsLen - 2 == i else self.__effectsPathsConfig.trajectoryRed
                CGF.loadGameObjectIntoHierarchy(modelPath, go, Math.Vector3(0, 0, 0), partial(cbTrajectoryModel, scale, rotation, translation))

            self.gameObjects.append(go)

        CGF.loadGameObject(self.__effectsPathsConfig.emptyGO, BigWorld.player().spaceID, Math.Vector3(0, 0, 0), cbEmptyTrajectory)

    def __spawnImpactPoint(self, hitPosition):

        def cbImpactPoint(go):
            self.__setTransformToGameObject(go, (1, 1, 1), (0, 0, 0), hitPosition)
            self.gameObjects.append(go)

        CGF.loadGameObject(self.__effectsPathsConfig.impactPoint, BigWorld.player().spaceID, Math.Vector3(0, 0, 0), cbImpactPoint)

    def __spawnSpacedArmorImpactPoint(self, hitPosition):

        def cbSpacedArmorImpactPoint(go):
            self.__setTransformToGameObject(go, (1, 1, 1), (0, 0, 0), hitPosition)
            self.gameObjects.append(go)

        CGF.loadGameObject(self.__effectsPathsConfig.spacedArmorImpactPoint, BigWorld.player().spaceID, Math.Vector3(0, 0, 0), cbSpacedArmorImpactPoint)

    def __spawnSpacedArmorLine(self, originPosition, hitPosition):

        def cbSpacedArmorLine(go):
            numberOfDots = originPosition.distTo(hitPosition) / _DOTS_SPACING
            spacingVector = (hitPosition - originPosition) / numberOfDots

            def cbSpacedArmorPoint(go):
                transformComponent = go.findComponentByType(GenericComponents.TransformComponent)
                self.__setTransformToGameObject(go, (1, 1, 1), (0, 0, 0), transformComponent.position)

            for dotIndex in range(int(numberOfDots)):
                finalPosition = originPosition + spacingVector * (dotIndex + 1)
                CGF.loadGameObjectIntoHierarchy(self.__effectsPathsConfig.spacedArmorLinePoint, go, finalPosition, cbSpacedArmorPoint)

            self.gameObjects.append(go)

        CGF.loadGameObject(self.__effectsPathsConfig.emptyGO, BigWorld.player().spaceID, Math.Vector3(0, 0, 0), cbSpacedArmorLine)

    def __spawnExplosionSphere(self, position, radius):

        def cbExplosionSphere(go):
            BigWorld.setEdgeDrawerImpenetratableZoneOverlay(0)
            BigWorld.setEdgeDrawerPenetratableZoneOverlay(0)
            self.__setTransformToGameObject(go, (radius, radius, radius), (0, 0, 0), position)
            self.gameObjects.append(go)

        CGF.loadGameObject(self.__effectsPathsConfig.explosionSphere, BigWorld.player().spaceID, Math.Vector3(0, 0, 0), cbExplosionSphere)

    def __spawnImpactZone(self, segments, vehicleAppearance, maxComponentIndex):

        def cbImpactZone(go):
            go.createComponent(ImpactZoneComponent, segments, vehicleAppearance, maxComponentIndex)
            self.gameObjects.append(go)

        CGF.loadGameObject(self.__effectsPathsConfig.emptyGO, BigWorld.player().spaceID, Math.Vector3(0, 0, 0), cbImpactZone)

    @staticmethod
    def __setTransformToGameObject(go, scale, rotation, position):
        transformComponent = go.findComponentByType(GenericComponents.TransformComponent)
        transformComponent.position = position
        transformComponent.scale = scale
        transformComponent.rotation = rotation
