# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/tooltips/birthday_lootbox_slot_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class BirthdayLootboxSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(BirthdayLootboxSlotModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(0)

    def setDescription(self, value):
        self._setString(0, value)

    def getProbability(self):
        return self._getReal(1)

    def setProbability(self, value):
        self._setReal(1, value)

    def getVehicleNames(self):
        return self._getArray(2)

    def setVehicleNames(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehicleNamesType():
        return unicode

    def getBonuses(self):
        return self._getArray(3)

    def setBonuses(self, value):
        self._setArray(3, value)

    @staticmethod
    def getBonusesType():
        return ItemBonusModel

    def _initialize(self):
        super(BirthdayLootboxSlotModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addRealProperty('probability', 0.0)
        self._addArrayProperty('vehicleNames', Array())
        self._addArrayProperty('bonuses', Array())
