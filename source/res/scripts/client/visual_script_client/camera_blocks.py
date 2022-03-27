# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/camera_blocks.py
import BigWorld
from constants import IS_VS_EDITOR
from visual_script import ASPECT
from visual_script.block import Block, Meta, InitParam, EDITOR_TYPE, buildStrKeysValue
from visual_script.dependency import dependencyImporter
from visual_script.slot_types import SLOT_TYPE
if not IS_VS_EDITOR:
    from helpers import dependency
    from skeletons.gui.battle_session import IBattleSessionProvider
AvatarInputHandler = dependencyImporter('AvatarInputHandler')

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
        return [ASPECT.CLIENT]


class CameraTransform(Block, CameraMeta):

    def __init__(self, *args, **kwargs):
        super(CameraTransform, self).__init__(*args, **kwargs)
        self._position = self._makeDataOutputSlot('position', SLOT_TYPE.VECTOR3, self._execute)
        self._direction = self._makeDataOutputSlot('direction', SLOT_TYPE.VECTOR3, self._execute)

    def _execute(self):
        self._position.setValue(BigWorld.camera().position)
        self._direction.setValue(BigWorld.camera().direction)


class IsPointOnScreen(Block, CameraMeta):

    def __init__(self, *args, **kwargs):
        super(IsPointOnScreen, self).__init__(*args, **kwargs)
        self._point = self._makeDataInputSlot('point', SLOT_TYPE.VECTOR3)
        self._isOnScreen = self._makeDataOutputSlot('isOnScreen', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        self._isOnScreen.setValue(AvatarInputHandler.cameras.isPointOnScreen(self._point.getValue()))


class MoveRTSCommanderCamera(Block, CameraMeta):
    _TARGET_POS_DIR = 'Position and Yaw'
    _TARGET_VEHICLE = 'Vehicle'
    _targets = [_TARGET_POS_DIR, _TARGET_VEHICLE]

    @classmethod
    def initParams(cls):
        return [InitParam('Target Type', SLOT_TYPE.STR, buildStrKeysValue(*cls._targets), EDITOR_TYPE.STR_KEY_SELECTOR)]

    def __init__(self, *args, **kwargs):
        super(MoveRTSCommanderCamera, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        targetType = self._getInitParams()
        if targetType == self._TARGET_POS_DIR:
            self._position = self._makeDataInputSlot('Position', SLOT_TYPE.VECTOR3)
            self._yaw = self._makeDataInputSlot('Yaw', SLOT_TYPE.ANGLE)
        elif targetType == self._TARGET_VEHICLE:
            self._vehicle = self._makeDataInputSlot('Vehicle', SLOT_TYPE.VEHICLE)
        self._out = self._makeEventOutputSlot('out')

    def validate(self):
        targetType = self._getInitParams()
        if targetType == self._TARGET_POS_DIR:
            if not self._position.hasValue():
                return 'Position is required'
        elif targetType == self._TARGET_VEHICLE:
            if not self._vehicle.hasValue():
                return 'Vehicle is required'
        else:
            return 'Wrong target type {}'.format(targetType)
        return super(MoveRTSCommanderCamera, self).validate()

    def _execute(self):
        if not IS_VS_EDITOR:
            sessionProvider = dependency.instance(IBattleSessionProvider)
            rtsCommander = sessionProvider.dynamic.rtsCommander
            targetType = self._getInitParams()
            if targetType == self._TARGET_POS_DIR:
                pos = self._position.getValue()
                if self._yaw.hasValue():
                    rtsCommander.setCameraPositionAndRotation(pos, self._yaw.getValue())
                else:
                    rtsCommander.setCameraPosition(pos)
            else:
                vehicle = self._vehicle.getValue()
                if vehicle is not None:
                    rtsCommander.moveToVehicle(vehicle.id)
        self._out.call()
        return
