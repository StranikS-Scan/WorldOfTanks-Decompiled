# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/tooltips/cosmic_lootbox_slot_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class SlotType(Enum):
    LOOTBOX = 'lootbox'


class CosmicLootboxSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(CosmicLootboxSlotModel, self).__init__(properties=properties, commands=commands)

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

    def getSlotType(self):
        return SlotType(self._getString(3))

    def setSlotType(self, value):
        self._setString(3, value.value)

    def getBonuses(self):
        return self._getArray(4)

    def setBonuses(self, value):
        self._setArray(4, value)

    @staticmethod
    def getBonusesType():
        return ItemBonusModel

    def _initialize(self):
        super(CosmicLootboxSlotModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addRealProperty('probability', 0.0)
        self._addArrayProperty('vehicleNames', Array())
        self._addStringProperty('slotType')
        self._addArrayProperty('bonuses', Array())
