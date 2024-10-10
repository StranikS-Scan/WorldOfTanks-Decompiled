# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_equipment_slot_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class WtEquipmentSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(WtEquipmentSlotModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(0)

    def setIcon(self, value):
        self._setResource(0, value)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getTooltipId(self):
        return self._getString(2)

    def setTooltipId(self, value):
        self._setString(2, value)

    def getIsInfinite(self):
        return self._getBool(3)

    def setIsInfinite(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(WtEquipmentSlotModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addNumberProperty('id', 0)
        self._addStringProperty('tooltipId', '')
        self._addBoolProperty('isInfinite', False)
