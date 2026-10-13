# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/shared/clip/unlimited_clip_model.py
from frameworks.wulf import ViewModel

class UnlimitedClipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(UnlimitedClipModel, self).__init__(properties=properties, commands=commands)

    def getIsUnlimitedClip(self):
        return self._getBool(0)

    def setIsUnlimitedClip(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(UnlimitedClipModel, self)._initialize()
        self._addBoolProperty('isUnlimitedClip', False)
