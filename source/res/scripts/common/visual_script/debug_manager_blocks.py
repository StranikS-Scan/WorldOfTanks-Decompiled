# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/debug_manager_blocks.py
import Math
from visual_script.slot_types import SLOT_TYPE, arrayOf
from debug_manager_blocks_base import DebugManagerBlock, DEFAULT_COLOR
from DebugManager import isGroupEnabled

class DebugManagerRegisterObject(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerRegisterObject, self).__init__(*args, **kwargs)

    def _groupAutoEnable(self):
        return True


class DebugManagerClearObject(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerClearObject, self).__init__(*args, **kwargs)

    def _groupAutoEnable(self):
        return True


class DebugManagerIsGroupEnabled(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerIsGroupEnabled, self).__init__(*args, **kwargs)
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.BOOL, self._execute)

    def _execute(self):
        groupID = self._slotGetValue('groupID')
        res = isGroupEnabled(groupID)
        self._res.setValue(res)

    def _eventSlotsEnabled(self):
        return False

    def _nameSlotEnabled(self):
        return False

    def _groupAutoEnable(self):
        return True


class DebugManagerRemoveObject(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerRemoveObject, self).__init__(*args, **kwargs)

    def _groupAutoEnable(self):
        return True


class DebugManagerRemoveGroup(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerRemoveGroup, self).__init__(*args, **kwargs)

    def _nameSlotEnabled(self):
        return False

    def _groupAutoEnable(self):
        return True


class DebugManagerShowMessage(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerShowMessage, self).__init__(*args, **kwargs)
        self._createDataInputSlot('value', SLOT_TYPE.STR)


class DebugManagerShowText2D(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerShowText2D, self).__init__(*args, **kwargs)
        self._createDataInputSlot('text', SLOT_TYPE.STR)
        self._createDataInputSlot('position', SLOT_TYPE.VECTOR2)
        self._createDataInputSlot('isPixels', SLOT_TYPE.BOOL, False)
        self._createDataInputSlot('color', SLOT_TYPE.COLOR, DEFAULT_COLOR)


class DebugManagerShowPoint2D(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerShowPoint2D, self).__init__(*args, **kwargs)
        self._createDataInputSlot('positions', arrayOf(SLOT_TYPE.VECTOR2))
        self._createDataInputSlot('isPixels', SLOT_TYPE.BOOL, False)
        self._createDataInputSlot('color', SLOT_TYPE.COLOR, DEFAULT_COLOR)


class DebugManagerShowLine2D(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerShowLine2D, self).__init__(*args, **kwargs)
        self._createDataInputSlot('positions', arrayOf(SLOT_TYPE.VECTOR2))
        self._createDataInputSlot('isLabel', SLOT_TYPE.BOOL, False)
        self._createDataInputSlot('isPixels', SLOT_TYPE.BOOL, False)
        self._createDataInputSlot('color', SLOT_TYPE.COLOR, DEFAULT_COLOR)


class DebugManagerShowCircle2D(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerShowCircle2D, self).__init__(*args, **kwargs)
        self._createDataInputSlot('center', SLOT_TYPE.VECTOR2)
        self._createDataInputSlot('radius', SLOT_TYPE.FLOAT)
        self._createDataInputSlot('isPixels', SLOT_TYPE.BOOL, False)
        self._createDataInputSlot('color', SLOT_TYPE.COLOR, DEFAULT_COLOR)


class DebugManagerShowRectangle2D(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerShowRectangle2D, self).__init__(*args, **kwargs)
        self._createDataInputSlot('start', SLOT_TYPE.VECTOR2)
        self._createDataInputSlot('end', SLOT_TYPE.VECTOR2)
        self._createDataInputSlot('isPixels', SLOT_TYPE.BOOL, False)
        self._createDataInputSlot('color', SLOT_TYPE.COLOR, DEFAULT_COLOR)


class DebugManagerShowText3D(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerShowText3D, self).__init__(*args, **kwargs)
        self._createDataInputSlot('info', SLOT_TYPE.DICTIONARY)
        self._createDataInputSlot('position', SLOT_TYPE.VECTOR3, Math.Vector3(0, 1, 0))
        self._createDataInputSlot('entityID', SLOT_TYPE.INT, -1)
        self._createDataInputSlot('color', SLOT_TYPE.COLOR, DEFAULT_COLOR)


class DebugManagerShowLine3D(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerShowLine3D, self).__init__(*args, **kwargs)
        self._createDataInputSlot('positions', arrayOf(SLOT_TYPE.VECTOR3))
        self._createDataInputSlot('entityID', SLOT_TYPE.INT, -1)
        self._createDataInputSlot('isArrow', SLOT_TYPE.BOOL, False)
        self._createDataInputSlot('color', SLOT_TYPE.COLOR, DEFAULT_COLOR)


class DebugManagerShowPoint3D(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerShowPoint3D, self).__init__(*args, **kwargs)
        self._createDataInputSlot('positions', arrayOf(SLOT_TYPE.VECTOR3))
        self._createDataInputSlot('entityID', SLOT_TYPE.INT, -1)
        self._createDataInputSlot('color', SLOT_TYPE.COLOR, DEFAULT_COLOR)


class DebugManagerShowBox3D(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerShowBox3D, self).__init__(*args, **kwargs)
        self._createDataInputSlot('center', SLOT_TYPE.VECTOR3)
        self._createDataInputSlot('direction', SLOT_TYPE.VECTOR3, Math.Vector3(0, 0, 1))
        self._createDataInputSlot('size', SLOT_TYPE.VECTOR3, Math.Vector3(1, 1, 1))
        self._createDataInputSlot('entityID', SLOT_TYPE.INT, -1)
        self._createDataInputSlot('color', SLOT_TYPE.COLOR, DEFAULT_COLOR)


class DebugManagerShowCircle3D(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerShowCircle3D, self).__init__(*args, **kwargs)
        self._createDataInputSlot('center', SLOT_TYPE.VECTOR3)
        self._createDataInputSlot('radius', SLOT_TYPE.FLOAT)
        self._createDataInputSlot('normal', SLOT_TYPE.VECTOR3, Math.Vector3(0, 1, 0))
        self._createDataInputSlot('entityID', SLOT_TYPE.INT, -1)
        self._createDataInputSlot('color', SLOT_TYPE.COLOR, DEFAULT_COLOR)


class DebugManagerShowSphere(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerShowSphere, self).__init__(*args, **kwargs)
        self._createDataInputSlot('center', SLOT_TYPE.VECTOR3)
        self._createDataInputSlot('radius', SLOT_TYPE.FLOAT)
        self._createDataInputSlot('entityID', SLOT_TYPE.INT, -1)
        self._createDataInputSlot('color', SLOT_TYPE.COLOR, DEFAULT_COLOR)


class DebugManagerShowCylinder(DebugManagerBlock):

    def __init__(self, *args, **kwargs):
        super(DebugManagerShowCylinder, self).__init__(*args, **kwargs)
        self._createDataInputSlot('start', SLOT_TYPE.VECTOR3)
        self._createDataInputSlot('end', SLOT_TYPE.VECTOR3)
        self._createDataInputSlot('radius', SLOT_TYPE.FLOAT)
        self._createDataInputSlot('entityID', SLOT_TYPE.INT, -1)
        self._createDataInputSlot('color', SLOT_TYPE.COLOR, DEFAULT_COLOR)
