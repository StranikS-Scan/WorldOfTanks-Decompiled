# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/camera.py
import BigWorld
from visual_script.block import Block, Meta, SLOT_TYPE, ASPECT
from visual_script_client.dependency import dependencyImporter
avatarInput, cameras = dependencyImporter('AvatarInputHandler', 'AvatarInputHandler.cameras')

class Camera(Meta):

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class IsCameraDynamic(Block, Camera):

    def __init__(self, *args, **kwargs):
        super(IsCameraDynamic, self).__init__(*args, **kwargs)
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.BOOL, IsCameraDynamic._isCameraDynamic)

    def _isCameraDynamic(self):
        self._res.setValue(avatarInput.AvatarInputHandler.isCameraDynamic())


class DefaultFov(Block, Camera):

    def __init__(self, *args, **kwargs):
        super(DefaultFov, self).__init__(*args, **kwargs)
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.ANGLE, DefaultFov._getDefaultFov)

    def _getDefaultFov(self):
        self._res.setValue(cameras.FovExtended.instance().actualDefaultVerticalFov)


class CurrentFov(Block, Camera):

    def __init__(self, *args, **kwargs):
        super(CurrentFov, self).__init__(*args, **kwargs)
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.ANGLE, CurrentFov._getCurrentFov)

    def _getCurrentFov(self):
        self._res.setValue(BigWorld.projection().fov)


class SetFovMultiplier(Block, Camera):

    def __init__(self, *args, **kwargs):
        super(SetFovMultiplier, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', SetFovMultiplier._onIn)
        self._key = self._makeDataInputSlot('key', SLOT_TYPE.STR)
        self._value = self._makeDataInputSlot('value', SLOT_TYPE.FLOAT)
        self._out = self._makeEventOutputSlot('out')

    def _onIn(self):
        cameras.FovExtended.instance().setExtraMultiplier(self._key.getValue(), self._value.getValue())
        self._out.call()


class GetFovMultiplier(Block, Camera):

    def __init__(self, *args, **kwargs):
        super(GetFovMultiplier, self).__init__(*args, **kwargs)
        self._key = self._makeDataInputSlot('key', SLOT_TYPE.STR)
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.FLOAT, GetFovMultiplier._getFovMultiplier)

    def _getFovMultiplier(self):
        self._res.setValue(cameras.FovExtended.instance().getExtraMultiplier(self._key.getValue()))


class RemoveFovMultiplier(Block, Camera):

    def __init__(self, *args, **kwargs):
        super(RemoveFovMultiplier, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', RemoveFovMultiplier._onIn)
        self._key = self._makeDataInputSlot('key', SLOT_TYPE.STR)
        self._out = self._makeEventOutputSlot('out')

    def _onIn(self):
        cameras.FovExtended.instance().remExtraMultiplier(self._key.getValue())
        self._out.call()
