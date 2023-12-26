# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/arena_camera_manager.py
import logging
import CGF
from GenericComponents import TransformComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from CameraComponents import CameraComponent
_logger = logging.getLogger(__name__)

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class ArenaCameraManager(CGF.ComponentManager):

    def __init__(self, *args):
        super(ArenaCameraManager, self).__init__(*args)
        self.__cameras = dict()

    def getCameraTransform(self, name):
        return self.__cameras.get(name)

    @onAddedQuery(CameraComponent, TransformComponent, tickGroup='PostHierarchy')
    def onCameraAdded(self, cameraComponent, transformComponent):
        if cameraComponent.name in self.__cameras:
            _logger.warning('Camera with the same name was already added: %s', cameraComponent.name)
            return
        self.__cameras[cameraComponent.name] = transformComponent.worldTransform

    @onRemovedQuery(CameraComponent)
    def onCameraRemoved(self, cameraComponent):
        if cameraComponent.name not in self.__cameras:
            _logger.warning('Camera with the same name already removed: %s', cameraComponent.name)
            return
        self.__cameras.pop(cameraComponent.name)
