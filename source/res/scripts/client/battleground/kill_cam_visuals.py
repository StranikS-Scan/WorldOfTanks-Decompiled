# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/kill_cam_visuals.py
import math
import logging
import typing
import BigWorld
import CGF
import Math
import math_utils
from typing import List
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
        self.__isActive = False
        self.__spaceID = None
        dynObjectsCache = dependency.instance(IBattleDynamicObjectsCache)
        self.__effectsPathsConfig = dynObjectsCache.getFeaturesConfig(_KillCamEffectDynObjects.CONFIG_NAME)
        return

    def destroy(self):
        _logger.info('[EffectsController] Destroy Kill Cam Effects')
        self.__isActive = False
        self.hideEdges()
        self.delayCallback(0.0, self.__removeGameObjects)

    def hideEdges(self):
        self.__removeEdgeDrawer()

    def displayKillCamEffects(self, vehicleAppearance, maxComponentIndex, hasProjectilePierced, hasNonPiercedDamage, isSPG, isSpotted, isShellHE, explosionRadius, trajectoryPoints, segments, impactPoint, isRicochet):
        _logger.info('displayKillCamEffects (params): %s %s %s %s %s %s %s %s %s %s %s', vehicleAppearance, maxComponentIndex, hasProjectilePierced, hasNonPiercedDamage, isSPG, isSpotted, isShellHE, explosionRadius, trajectoryPoints, segments, impactPoint)
        self.__isActive = True
        self.__spaceID = BigWorld.player().spaceID
        if trajectoryPoints[-1] != impactPoint:
            self.__spawnSpacedArmorLine(trajectoryPoints[-1], impactPoint)
            self.__spawnSpacedArmorImpactPoint(trajectoryPoints[-1])
        if not hasProjectilePierced and not hasNonPiercedDamage and not isShellHE:
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
            if go.hasComponent(HighlightComponent):
                go.removeComponent(HighlightComponent)

    def __removeGameObjects(self):
        for go in self.gameObjects:
            _logger.info('[EffectsController] Remove - %s', go)
            go.destroy()

        self.gameObjects = []

    def __getLoadCallback(self, callback):

        def callbackWrapper(objects, queue):
            root = objects[0]
            if not self.__isActive:
                return False
            self.gameObjects.append(queue.gameObject(root))
            callback(objects, queue)
            return True

        return callbackWrapper

    def __spawnHitCone(self, hitPosition, originPosition):

        def cbHitCone(objects, queue):
            root = objects[0]
            direction = Math.Vector3(hitPosition - originPosition)
            rotation = Math.Vector3(direction.yaw, direction.pitch, 0)
            maximumPitch = math.radians(_UNSPOTTED_CONE_MAX_PITCH)
            pitch = math_utils.clamp(-maximumPitch, 0, rotation.y)
            rotation = Math.Vector3(rotation.x, pitch, rotation.z)
            self.__setTransformToGameObject(root, queue, (1, 1, 1), rotation, originPosition)

        CGF.loadAndCreatePrefab(self.__effectsPathsConfig.cone, self.__spaceID, Math.Vector3(0, 0, 0), self.__getLoadCallback(cbHitCone))

    def __spawnShellTrajectory(self, points, isSpgShot=False, isRicochet=False):

        def cbEmptyTrajectory(objects, queue):

            def cbTrajectoryModel(scale, rotation, position, objects, queue):
                self.__setTransformToGameObject(objects[0], queue, scale, rotation, position)

            if not isSpgShot and not isRicochet:
                lastPoint = points[-1]
                prevPoint = points[-2]
                gradientPoint = (prevPoint - lastPoint) * 0.1 + lastPoint
                points.insert(-1, gradientPoint)
            ptsLen = len(points)
            root = objects[0]
            parentUUID = queue.gameObjectUuid(root)
            for i in range(ptsLen - 1):
                direction = Math.Vector3(points[i + 1] - points[i])
                translation = points[i]
                scale = (LINE_WIDTH, LINE_WIDTH, direction.length / _LENGTH_FACTOR)
                rotation = Math.Vector3(direction.yaw, direction.pitch, 0)
                modelPath = self.__effectsPathsConfig.trajectoryGradient if ptsLen - 2 == i else self.__effectsPathsConfig.trajectoryRed
                CGF.loadAndCreatePrefabWithParentUUID(modelPath, self.__spaceID, parentUUID, Math.Vector3(0, 0, 0), self.__getLoadCallback(partial(cbTrajectoryModel, scale, rotation, translation)))

        CGF.loadAndCreatePrefab(self.__effectsPathsConfig.emptyGO, self.__spaceID, Math.Vector3(0, 0, 0), self.__getLoadCallback(cbEmptyTrajectory))

    def __spawnImpactPoint(self, hitPosition):

        def cbImpactPoint(objects, queue):
            self.__setTransformToGameObject(objects[0], queue, (1, 1, 1), (0, 0, 0), hitPosition)

        CGF.loadAndCreatePrefab(self.__effectsPathsConfig.impactPoint, self.__spaceID, Math.Vector3(0, 0, 0), self.__getLoadCallback(cbImpactPoint))

    def __spawnSpacedArmorImpactPoint(self, hitPosition):

        def cbSpacedArmorImpactPoint(objects, queue):
            self.__setTransformToGameObject(objects[0], queue, (1, 1, 1), (0, 0, 0), hitPosition)

        CGF.loadAndCreatePrefab(self.__effectsPathsConfig.spacedArmorImpactPoint, self.__spaceID, Math.Vector3(0, 0, 0), self.__getLoadCallback(cbSpacedArmorImpactPoint))

    def __spawnSpacedArmorLine(self, originPosition, hitPosition):

        def cbSpacedArmorLine(objects, queue):
            numberOfDots = originPosition.distTo(hitPosition) / _DOTS_SPACING
            spacingVector = (hitPosition - originPosition) / numberOfDots

            def cbSpacedArmorPoint(objects, queue):
                root = objects[0]
                transformComponent = queue.component(root, CGF.TransformComponent)
                self.__setTransformToGameObject(root, queue, (1, 1, 1), (0, 0, 0), transformComponent.position)

            parentUUID = queue.gameObjectUuid(objects[0])
            for dotIndex in range(int(numberOfDots)):
                finalPosition = originPosition + spacingVector * (dotIndex + 1)
                CGF.loadAndCreatePrefabWithParentUUID(self.__effectsPathsConfig.spacedArmorLinePoint, self.__spaceID, parentUUID, finalPosition, self.__getLoadCallback(cbSpacedArmorPoint))

        CGF.loadAndCreatePrefab(self.__effectsPathsConfig.emptyGO, self.__spaceID, Math.Vector3(0, 0, 0), self.__getLoadCallback(cbSpacedArmorLine))

    def __spawnExplosionSphere(self, position, radius):

        def cbExplosionSphere(objects, queue):
            BigWorld.setEdgeDrawerImpenetratableZoneOverlay(0)
            BigWorld.setEdgeDrawerPenetratableZoneOverlay(0)
            self.__setTransformToGameObject(objects[0], queue, (radius, radius, radius), (0, 0, 0), position)

        CGF.loadAndCreatePrefab(self.__effectsPathsConfig.explosionSphere, self.__spaceID, Math.Vector3(0, 0, 0), self.__getLoadCallback(cbExplosionSphere))

    def __spawnImpactZone(self, segments, vehicleAppearance, maxComponentIndex):

        def cbImpactZone(objects, queue):
            root = objects[0]
            queue.createComponent(root, ImpactZoneComponent, segments, vehicleAppearance, maxComponentIndex)

        CGF.loadAndCreatePrefab(self.__effectsPathsConfig.emptyGO, self.__spaceID, Math.Vector3(0, 0, 0), self.__getLoadCallback(cbImpactZone))

    @staticmethod
    def __setTransformToGameObject(pending, queue, scale, rotationYPR, position):
        transformComponent = queue.component(pending, CGF.TransformComponent)
        transformComponent.position = position
        transformComponent.scale = scale
        transformComponent.rotationYPR = rotationYPR
