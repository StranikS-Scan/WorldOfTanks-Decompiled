# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/box_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.slot_model import SlotModel

class BoxModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BoxModel, self).__init__(properties=properties, commands=commands)

    def getCategory(self):
        return self._getString(0)

    def setCategory(self, value):
        self._setString(0, value)

    def getGuaranteedLimit(self):
        return self._getNumber(1)

    def setGuaranteedLimit(self, value):
        self._setNumber(1, value)

    def getSlots(self):
        return self._getArray(2)

    def setSlots(self, value):
        self._setArray(2, value)

    @staticmethod
    def getSlotsType():
        return SlotModel

    def _initialize(self):
        super(BoxModel, self)._initialize()
        self._addStringProperty('category', '')
        self._addNumberProperty('guaranteedLimit', 0)
        self._addArrayProperty('slots', Array())
