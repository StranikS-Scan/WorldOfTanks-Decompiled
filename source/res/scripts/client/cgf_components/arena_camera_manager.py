# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/arena_camera_manager.py
from __future__ import absolute_import
import logging
import CGF
from CameraComponents import CameraComponent
_logger = logging.getLogger(__name__)

class ArenaCameraSystem(CGF.System):
    CameraActivated = CGF.ActivateReaction(CGF.TransformComponent, CGF.ReactRo(CameraComponent))
    CameraDeactivated = CGF.DeactivateReaction(CGF.ReactRo(CameraComponent))
    Reactions = CGF.Reactions(CameraActivated, CameraDeactivated)

    def __init__(self, *args):
        super(ArenaCameraSystem, self).__init__(*args)
        self.__cameras = {}

    def update(self):
        for cameraComponent in self.reaction(self.CameraDeactivated):
            self.onCameraRemoved(cameraComponent)

        for transformComponent, cameraComponent in self.reaction(self.CameraActivated):
            self.onCameraAdded(cameraComponent, transformComponent)

    def getCameraTransform(self, name):
        return self.__cameras.get(name)

    def onCameraAdded(self, cameraComponent, transformComponent):
        if cameraComponent.name in self.__cameras:
            _logger.warning('Camera with the same name was already added: %s', cameraComponent.name)
            return
        self.__cameras[cameraComponent.name] = transformComponent.worldTransform

    def onCameraRemoved(self, cameraComponent):
        if cameraComponent.name not in self.__cameras:
            _logger.warning('Camera with the same name already removed: %s', cameraComponent.name)
            return
        else:
            self.__cameras.pop(cameraComponent.name, None)
            return
