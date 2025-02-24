# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/camera_blocks.py
from visual_script import ASPECT
from visual_script.block import Block, Meta
from visual_script.dependency import dependencyImporter
from visual_script.slot_types import SLOT_TYPE
utils, dependency, cameras, hangar_camera_manager, CGF = dependencyImporter('skeletons.gui.shared.utils', 'helpers.dependency', 'AvatarInputHandler.cameras', 'cgf_components.hangar_camera_manager', 'CGF')

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
        _, position = cameras.getWorldRayAndPosition()
        self._position.setValue(position)

    def _getDirection(self):
        direction, _ = cameras.getWorldRayAndPosition()
        direction.normalise()
        self._direction.setValue(direction)


class SwitchCamera(Block, CameraMeta):

    def __init__(self, *args, **kwargs):
        super(SwitchCamera, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._cameraName = self._makeDataInputSlot('cameraName', SLOT_TYPE.STR)
        self._spaceId = self._makeDataInputSlot('spaceId', SLOT_TYPE.INT)
        self._instantly = self._makeDataInputSlot('instantly', SLOT_TYPE.BOOL)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        cameraName = self._cameraName.getValue()
        spaceId = self._spaceId.getValue()
        cameraManager = CGF.getManager(spaceId, hangar_camera_manager.HangarCameraManager)
        if cameraManager:
            cameraManager.switchByCameraName(cameraName, self._instantly.getValue())
        self._out.call()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.HANGAR]


class OnCameraSwitched(Block, CameraMeta):

    def __init__(self, *args, **kwargs):
        super(OnCameraSwitched, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._initialize)
        self._spaceID = self._makeDataInputSlot('spaceID', SLOT_TYPE.INT)
        self._out = self._makeEventOutputSlot('out')
        self._cameraName = self._makeDataOutputSlot('cameraName', SLOT_TYPE.STR, None)
        return

    def _initialize(self):
        cameraManager = CGF.getManager(self._spaceID.getValue(), hangar_camera_manager.HangarCameraManager)
        if cameraManager:
            cameraManager.onCameraSwitched += self._onCameraSwitched

    def _onCameraSwitched(self, cameraName):
        self._cameraName.setValue(cameraName)
        self._out.call()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.HANGAR]


class GetCameraName(Block, CameraMeta):

    def __init__(self, *args, **kwargs):
        super(GetCameraName, self).__init__(*args, **kwargs)
        self._spaceId = self._makeDataInputSlot('spaceId', SLOT_TYPE.INT)
        self._cameraName = self._makeDataOutputSlot('cameraName', SLOT_TYPE.STR, self._execute)

    def _execute(self):
        spaceId = self._spaceId.getValue()
        cameraManager = CGF.getManager(spaceId, hangar_camera_manager.HangarCameraManager)
        if cameraManager:
            self._cameraName.setValue(cameraManager.getCurrentCameraName())

    @classmethod
    def blockAspects(cls):
        return [ASPECT.HANGAR]
