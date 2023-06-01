# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/hangar_blocks.py
from visual_script import ASPECT
from visual_script.block import Block, Meta
from visual_script.dependency import dependencyImporter
from visual_script.slot_types import SLOT_TYPE
utils, dependency, CGF, hangar_camera_manager = dependencyImporter('skeletons.gui.shared.utils', 'helpers.dependency', 'CGF', 'cgf_components.hangar_camera_manager')

class HangarCameraMeta(Meta):

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
        return [ASPECT.HANGAR]


class GetCamera(Block, HangarCameraMeta):
    hangarSpace = dependency.descriptor(utils.IHangarSpace)

    def __init__(self, *args, **kwargs):
        super(GetCamera, self).__init__(*args, **kwargs)
        self._position = self._makeDataOutputSlot('position', SLOT_TYPE.VECTOR3, self._getPosition)
        self._direction = self._makeDataOutputSlot('direction', SLOT_TYPE.VECTOR3, self._getDirection)

    def _getPosition(self):
        cameraManager = CGF.getManager(self.hangarSpace.spaceID, hangar_camera_manager.HangarCameraManager)
        if cameraManager:
            self._position.setValue(cameraManager.getCurrentCameraPosition())

    def _getDirection(self):
        cameraManager = CGF.getManager(self.hangarSpace.spaceID, hangar_camera_manager.HangarCameraManager)
        if cameraManager:
            self._direction.setValue(cameraManager.getCurrentCameraDirection())
