# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/details_item_model.py
from frameworks.wulf import ViewModel

class DetailsItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(DetailsItemModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getBlockIdx(self):
        return self._getNumber(1)

    def setBlockIdx(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(DetailsItemModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('blockIdx', 0)
