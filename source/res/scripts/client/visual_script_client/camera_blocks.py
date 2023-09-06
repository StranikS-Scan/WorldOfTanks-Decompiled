# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/camera_blocks.py
from constants import IS_VS_EDITOR
from visual_script import ASPECT
from visual_script.block import Block, Meta
from visual_script.dependency import dependencyImporter
from visual_script.slot_types import SLOT_TYPE
if not IS_VS_EDITOR:
    from helpers import isPlayerAccount
utils, dependency, CGF, hangar_camera_manager, cameras = dependencyImporter('skeletons.gui.shared.utils', 'helpers.dependency', 'CGF', 'cgf_components.hangar_camera_manager', 'AvatarInputHandler.cameras')

class CameraMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.HANGAR, ASPECT.CLIENT]


class GetCamera(Block, CameraMeta):
    hangarSpace = dependency.descriptor(utils.IHangarSpace)

    def __init__(self, *args, **kwargs):
        super(GetCamera, self).__init__(*args, **kwargs)
        self._position = self._makeDataOutputSlot('position', SLOT_TYPE.VECTOR3, self._getPosition)
        self._direction = self._makeDataOutputSlot('direction', SLOT_TYPE.VECTOR3, self._getDirection)

    def _getPosition(self):
        if isPlayerAccount():
            cameraManager = CGF.getManager(self.hangarSpace.spaceID, hangar_camera_manager.HangarCameraManager)
            if cameraManager:
                self._position.setValue(cameraManager.getCurrentCameraPosition())
        else:
            _, position = cameras.getWorldRayAndPosition()
            self._position.setValue(position)

    def _getDirection(self):
        if isPlayerAccount():
            cameraManager = CGF.getManager(self.hangarSpace.spaceID, hangar_camera_manager.HangarCameraManager)
            if cameraManager:
                self._direction.setValue(cameraManager.getCurrentCameraDirection())
        else:
            direction, _ = cameras.getWorldRayAndPosition()
            direction.normalise()
            self._direction.setValue(direction)
