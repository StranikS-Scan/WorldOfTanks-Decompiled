# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/event/ift_item_model.py
from frameworks.wulf import ViewModel

class IftItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(IftItemModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getPrice(self):
        return self._getNumber(3)

    def setPrice(self, value):
        self._setNumber(3, value)

    def getAmount(self):
        return self._getString(4)

    def setAmount(self, value):
        self._setString(4, value)

    def getAvailable(self):
        return self._getNumber(5)

    def setAvailable(self, value):
        self._setNumber(5, value)

    def getHighlight(self):
        return self._getString(6)

    def setHighlight(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(IftItemModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('price', 0)
        self._addStringProperty('amount', '')
        self._addNumberProperty('available', 0)
        self._addStringProperty('highlight', '')
