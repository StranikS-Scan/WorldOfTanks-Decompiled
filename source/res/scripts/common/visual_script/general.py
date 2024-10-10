# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/general.py
from block import Block, makeResEditorData, InitParam
from slot_types import SLOT_TYPE, arrayOf
from uuid_utils import genUUID

class ResourceSelector(Block):

    def __init__(self, *args, **kwargs):
        super(ResourceSelector, self).__init__(*args, **kwargs)
        root, ext = self._getInitParams()
        self._res = self._makeDataInputSlot('res', SLOT_TYPE.RESOURCE)
        self._res.setEditorData(makeResEditorData(root, ext))
        self._out = self._makeDataOutputSlot('out', SLOT_TYPE.RESOURCE, self._exec)

    def _exec(self):
        self._out.setValue(self._res.getValue())

    @classmethod
    def initParams(cls):
        return [InitParam('root', SLOT_TYPE.STR, 'wot'), InitParam('ext', SLOT_TYPE.STR, 'xml')]


class GenerateUniqueString(Block):

    def __init__(self, *args, **kwargs):
        super(GenerateUniqueString, self).__init__(*args, **kwargs)
        self._prefix = self._makeDataInputSlot('prefix', SLOT_TYPE.STR)
        self._res = self._makeDataOutputSlot('res', SLOT_TYPE.STR, self._getData)

    @classmethod
    def hasValidation(cls):
        return True

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    def _getData(self):
        prefix = self._prefix.getValue() if self._prefix.hasValue() else ''
        self._res.setValue('{prefix}_{ts}'.format(prefix=prefix, ts=genUUID().time))


class SplitString(Block):

    def __init__(self, *args, **kwargs):
        super(SplitString, self).__init__(*args, **kwargs)
        self._fullstring = self._makeDataInputSlot('string', SLOT_TYPE.STR)
        self._split = self._makeDataInputSlot('char', SLOT_TYPE.STR)
        self._res = self._makeDataOutputSlot('res', arrayOf(SLOT_TYPE.STR), self._getData)

    @classmethod
    def hasValidation(cls):
        return True

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    def _getData(self):
        prefix = self._fullstring.getValue() if self._fullstring.hasValue() else ''
        char = self._split.getValue() if self._split.hasValue() else ''
        self._res.setValue(prefix.split(char))
