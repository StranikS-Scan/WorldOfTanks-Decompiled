# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/battle_royale_equipment_model.py
from frameworks.wulf import ViewModel

class BattleRoyaleEquipmentModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(BattleRoyaleEquipmentModel, self).__init__(properties=properties, commands=commands)

    def getIconName(self):
        return self._getString(0)

    def setIconName(self, value):
        self._setString(0, value)

    def getIntCD(self):
        return self._getNumber(1)

    def setIntCD(self, value):
        self._setNumber(1, value)

    def getQuantity(self):
        return self._getNumber(2)

    def setQuantity(self, value):
        self._setNumber(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getCooldownSeconds(self):
        return self._getNumber(4)

    def setCooldownSeconds(self, value):
        self._setNumber(4, value)

    def getTitle(self):
        return self._getString(5)

    def setTitle(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(BattleRoyaleEquipmentModel, self)._initialize()
        self._addStringProperty('iconName', '')
        self._addNumberProperty('intCD', 0)
        self._addNumberProperty('quantity', 0)
        self._addStringProperty('description', '')
        self._addNumberProperty('cooldownSeconds', 0)
        self._addStringProperty('title', '')
