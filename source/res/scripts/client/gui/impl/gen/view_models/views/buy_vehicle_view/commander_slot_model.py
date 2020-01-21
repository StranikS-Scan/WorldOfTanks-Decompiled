# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/buy_vehicle_view/commander_slot_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class CommanderSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(CommanderSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def actionPrice(self):
        return self._getViewModel(0)

    def getIdx(self):
        return self._getNumber(1)

    def setIdx(self, value):
        self._setNumber(1, value)

    def getIsSelected(self):
        return self._getBool(2)

    def setIsSelected(self, value):
        self._setBool(2, value)

    def getPercents(self):
        return self._getNumber(3)

    def setPercents(self, value):
        self._setNumber(3, value)

    def getTitle(self):
        return self._getString(4)

    def setTitle(self, value):
        self._setString(4, value)

    def getDefPrice(self):
        return self._getString(5)

    def setDefPrice(self, value):
        self._setString(5, value)

    def getIsFree(self):
        return self._getBool(6)

    def setIsFree(self, value):
        self._setBool(6, value)

    def getDiscount(self):
        return self._getNumber(7)

    def setDiscount(self, value):
        self._setNumber(7, value)

    def getSlotIsEnabled(self):
        return self._getBool(8)

    def setSlotIsEnabled(self, value):
        self._setBool(8, value)

    def getIsBootcamp(self):
        return self._getBool(9)

    def setIsBootcamp(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(CommanderSlotModel, self)._initialize()
        self._addViewModelProperty('actionPrice', ListModel())
        self._addNumberProperty('idx', 0)
        self._addBoolProperty('isSelected', False)
        self._addNumberProperty('percents', 0)
        self._addStringProperty('title', '')
        self._addStringProperty('defPrice', '')
        self._addBoolProperty('isFree', False)
        self._addNumberProperty('discount', -1)
        self._addBoolProperty('slotIsEnabled', True)
        self._addBoolProperty('isBootcamp', False)
