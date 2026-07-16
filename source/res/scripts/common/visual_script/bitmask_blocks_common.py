# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/bitmask_blocks_common.py
from __future__ import absolute_import
from future.utils import viewitems
from past.builtins import long, xrange
from visual_script.block import Block, InitParam, buildStrKeysValue, Meta
from visual_script.misc import errorVScript, EDITOR_TYPE, BLOCK_MODE
from visual_script.slot_types import SLOT_TYPE

class BitMaskMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass


class BitMaskBase(Block, BitMaskMeta):
    _MASK_TYPES = {}

    def __init__(self, *args, **kwargs):
        super(BitMaskBase, self).__init__(*args, **kwargs)
        self._flags = []
        flagsCount, bitMaskType = self._getInitParams()
        type = self._MASK_TYPES[bitMaskType]
        self._inFlags = {name:getattr(type, name) for name, value in viewitems(type.__dict__) if not name.startswith('_')}
        for _ in xrange(flagsCount):
            self._addInputNode()

        self._bitMask = self._makeDataOutputSlot(bitMaskType, SLOT_TYPE.INT, self._getValue)

    def _addInputNode(self):
        self._flags.append(self._makeDataInputSlot('f' + str(len(self._flags)), SLOT_TYPE.STR, EDITOR_TYPE.ENUM_SELECTOR))
        self._flags[-1].setEditorData(list(self._inFlags))

    @classmethod
    def initParams(cls):
        return [InitParam('Flags Count', SLOT_TYPE.INT, 1), InitParam('BitMask type', SLOT_TYPE.STR, buildStrKeysValue(*cls._MASK_TYPES.keys()), EDITOR_TYPE.STR_KEY_SELECTOR)]

    def _getValue(self):
        bitMask = 0
        for f in self._flags:
            if f.hasValue():
                bitMask |= self._inFlags[f.getValue()]
            errorVScript(self, 'Not all input flags are specified')

        self._bitMask.setValue(bitMask)


class BitwiseOperationBase(Block, BitMaskMeta):

    def __init__(self, *args, **kwargs):
        super(BitwiseOperationBase, self).__init__(*args, **kwargs)
        self._masks = []
        masksCount = self._getInitParams()
        for _ in xrange(masksCount):
            self._addInputNode()

        self._addOutputNode()

    @classmethod
    def initParams(cls):
        return [InitParam('Masks Count', SLOT_TYPE.INT, 1)]

    @property
    def _maskValues(self):
        return [ long(m.getValue()) for m in self._masks ]

    def _addInputNode(self):
        self._masks.append(self._makeDataInputSlot('m' + str(len(self._masks)), SLOT_TYPE.INT))

    def _addOutputNode(self):
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.INT, self._getValue)

    def _getValue(self):
        raise NotImplementedError

    @classmethod
    def mode(cls):
        return Block.mode() | BLOCK_MODE.CAN_BE_CONST_EXPR
