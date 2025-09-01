# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/camera_mover.py
from __future__ import absolute_import
import math
import CGF
from CameraComponents import OrbitComponent
from GenericComponents import TransformComponent
from gui.subhangar.subhangar_state_groups import CameraMover
from helpers import dependency
from math_utils import reduceToPI
from skeletons.gui.shared.utils import IHangarSpace

class VehicleHubCameraMover(CameraMover):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, transitionDuration):
        self._moveInstantly = True
        self._transitionDuration = transitionDuration

    def moveCamera(self, cameraManager, cameraName):
        moveInstantly = self._moveInstantly
        self._moveInstantly = False
        if moveInstantly:
            cameraManager.switchByCameraName(cameraName, instantly=True)
            return
        cameraManager.switchByCameraName(cameraName, instantly=True, resetTransform=False, forceUpdate=False)
        cameraGo = cameraManager.findCameraGameObjectByName(cameraName)
        if not cameraGo:
            cameraManager.switchByCameraName(cameraName, instantly=True)
            return
        hierarchy = CGF.HierarchyManager(self.__hangarSpace.spaceID)
        parentTransformComponent = hierarchy.getParent(cameraGo).findComponentByType(TransformComponent)
        orbitComponent = cameraGo.findComponentByType(OrbitComponent)
        if not orbitComponent or not parentTransformComponent:
            cameraManager.switchByCameraName(cameraName, instantly=True)
            return
        worldYaw = parentTransformComponent.worldTransform.yaw
        worldPitch = parentTransformComponent.worldTransform.pitch
        yaw = reduceToPI(orbitComponent.currentYaw + worldYaw + math.pi)
        pitch = reduceToPI(orbitComponent.currentPitch + worldPitch)
        targetPos = parentTransformComponent.worldTransform.translation
        distConstraints = orbitComponent.distLimits
        cameraManager.moveCamera(targetPos, yaw, pitch, distance=orbitComponent.currentDist, duration=self._transitionDuration, distConstraints=distConstraints)
