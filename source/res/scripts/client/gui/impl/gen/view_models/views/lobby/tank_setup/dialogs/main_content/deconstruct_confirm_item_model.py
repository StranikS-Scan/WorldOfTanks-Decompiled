# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/main_content/deconstruct_confirm_item_model.py
from frameworks.wulf import ViewModel

class DeconstructConfirmItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(DeconstructConfirmItemModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getString(1)

    def setValue(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getLevel(self):
        return self._getNumber(3)

    def setLevel(self, value):
        self._setNumber(3, value)

    def getIntCD(self):
        return self._getNumber(4)

    def setIntCD(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(DeconstructConfirmItemModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('value', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('level', 1)
        self._addNumberProperty('intCD', 0)
