# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/shared/clip/extra_shot_clip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ClipState(Enum):
    NONE = 'none'
    NORMAL = 'normal'
    CRITICAL = 'critical'


class ExtraShotClipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ExtraShotClipModel, self).__init__(properties=properties, commands=commands)

    def getClipCapacity(self):
        return self._getNumber(0)

    def setClipCapacity(self, value):
        self._setNumber(0, value)

    def getQuantityInClip(self):
        return self._getNumber(1)

    def setQuantityInClip(self, value):
        self._setNumber(1, value)

    def getClipState(self):
        return ClipState(self._getString(2))

    def setClipState(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(ExtraShotClipModel, self)._initialize()
        self._addNumberProperty('clipCapacity', -1)
        self._addNumberProperty('quantityInClip', -1)
        self._addStringProperty('clipState', ClipState.NONE.value)
