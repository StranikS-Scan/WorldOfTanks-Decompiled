# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/debug_manager_blocks_base.py
from visual_script.block import Block, Meta
from visual_script.misc import ASPECT, errorVScript
from visual_script.slot_types import SLOT_TYPE, arrayOf
import DebugManager
from DebugManager import COLORS, isGroupEnabled, setGroupEnabled

def uint32toInt32(value):
    if value <= 2147483647:
        return value
    else:
        return -(4294967295L - value + 1)


def int32ToUint32(value):
    if value >= 0:
        return value
    else:
        return 4294967295L + value + 1


DEFAULT_COLOR = uint32toInt32(COLORS.DEFAULT)

class DebugManagerBlockMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER, ASPECT.HANGAR]


class DebugManagerBlock(Block, DebugManagerBlockMeta):

    def __init__(self, *args, **kwargs):
        super(DebugManagerBlock, self).__init__(*args, **kwargs)
        self._params = []
        self._func = self.__class__.__name__[len('DebugManager'):]
        self._func = self._func[:1].lower() + self._func[1:]
        if self._eventSlotsEnabled():
            self._in = self._makeEventInputSlot('in', self._execute)
            self._out = self._makeEventOutputSlot('out')
        self._createDataInputSlot('groupID', SLOT_TYPE.STR)
        if self._nameSlotEnabled():
            self._createDataInputSlot('name', SLOT_TYPE.STR)

    def _execute(self):
        if hasattr(DebugManager, self._func):
            func = getattr(DebugManager, self._func)
            params = {}
            for slotName in self._params:
                slotValue = self._slotGetValue(slotName)
                params[slotName] = slotValue

            func(**params)
            if self._groupAutoEnable():
                groupID = self._slotGetValue('groupID')
                if not isGroupEnabled(groupID):
                    setGroupEnabled(groupID, True)
        else:
            errorVScript(self, 'Unknown DebugManager function {}'.format(self._func))
        self._out.call()

    def _createDataInputSlot(self, slotName, slotType=SLOT_TYPE.STR, slotDefaultValue=None):
        setattr(self, '_' + slotName, self._makeDataInputSlot(slotName, slotType))
        if slotDefaultValue is not None:
            getattr(self, '_' + slotName).setDefaultValue(slotDefaultValue)
        self._params.append(slotName)
        return

    def _eventSlotsEnabled(self):
        return True

    def _nameSlotEnabled(self):
        return True

    def _groupAutoEnable(self):
        return True

    def _slotGetValue(self, slotName):
        slot = getattr(self, '_' + slotName)
        slotValue = slot.getValue()
        if slotName == 'entityID' and slotValue < 0:
            slotValue = None
        if slotName == 'color':
            slotValue = int32ToUint32(slotValue)
        return slotValue

    def captionText(self):
        return 'DebugManager: ' + self._func
