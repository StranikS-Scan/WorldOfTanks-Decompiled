# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/camera_blocks.py
import BigWorld
from dependency import dependencyImporter, editorValue
from visual_script.component import Component, InputSlot, OutputSlot, SLOT_TYPE, ASPECT
avatarInput, cameras = dependencyImporter('AvatarInputHandler', 'AvatarInputHandler.cameras')

class IsCameraDynamic(Component):

    @classmethod
    def componentCategory(cls):
        pass

    @classmethod
    def componentAspects(cls):
        return [ASPECT.CLIENT]

    def slotDefinitions(self):
        return [OutputSlot('res', SLOT_TYPE.BOOL, IsCameraDynamic._execute)]

    @editorValue(False)
    def _execute(self):
        return avatarInput.AvatarInputHandler.isCameraDynamic()


class DefaultFov(Component):

    @classmethod
    def componentCategory(cls):
        pass

    @classmethod
    def componentAspects(cls):
        return [ASPECT.CLIENT]

    def slotDefinitions(self):
        return [OutputSlot('res', SLOT_TYPE.ANGLE, DefaultFov._execute)]

    @editorValue(0)
    def _execute(self):
        return cameras.FovExtended.instance().actualDefaultVerticalFov


class CurrentFov(Component):

    @classmethod
    def componentCategory(cls):
        pass

    @classmethod
    def componentAspects(cls):
        return [ASPECT.CLIENT]

    def slotDefinitions(self):
        return [OutputSlot('res', SLOT_TYPE.ANGLE, CurrentFov._execute)]

    def _execute(self):
        return BigWorld.projection().fov


class SetFovMultiplier(Component):

    @classmethod
    def componentCategory(cls):
        pass

    @classmethod
    def componentAspects(cls):
        return [ASPECT.CLIENT]

    def slotDefinitions(self):
        return [InputSlot('in', SLOT_TYPE.EVENT, SetFovMultiplier._execute),
         InputSlot('key', SLOT_TYPE.STR, None),
         InputSlot('value', SLOT_TYPE.FLOAT, None),
         OutputSlot('out', SLOT_TYPE.EVENT, None)]

    @editorValue('out')
    def _execute(self, key, value):
        cameras.FovExtended.instance().setExtraMultiplier(key, value)


class GetFovMultiplier(Component):

    @classmethod
    def componentCategory(cls):
        pass

    @classmethod
    def componentAspects(cls):
        return [ASPECT.CLIENT]

    def slotDefinitions(self):
        return [InputSlot('key', SLOT_TYPE.STR, None), OutputSlot('res', SLOT_TYPE.FLOAT, GetFovMultiplier._execute)]

    @editorValue(1)
    def _execute(self, key):
        return cameras.FovExtended.instance().getExtraMultiplier(key)


class RemoveFovMultiplier(Component):

    @classmethod
    def componentCategory(cls):
        pass

    @classmethod
    def componentAspects(cls):
        return [ASPECT.CLIENT]

    def slotDefinitions(self):
        return [InputSlot('in', SLOT_TYPE.EVENT, RemoveFovMultiplier._execute), InputSlot('key', SLOT_TYPE.STR, None), OutputSlot('out', SLOT_TYPE.EVENT, None)]

    @editorValue('out')
    def _execute(self, key):
        cameras.FovExtended.instance().remExtraMultiplier(key)
