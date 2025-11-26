# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/components/loadout/battle_abilities_setup_model.py
from frameworks.wulf import Array
from frontline.gui.impl.gen.view_models.views.lobby.components.loadout.battle_ability_details import BattleAbilityDetails
from frontline.gui.impl.gen.view_models.views.lobby.components.loadout.battle_ability_slot_model import BattleAbilitySlotModel
from gui.impl.gen.view_models.views.lobby.loadout.base_loadout_model import BaseLoadoutModel

class BattleAbilitiesSetupModel(BaseLoadoutModel):
    __slots__ = ('onCurrentAbilityLevelChanged', 'onApplyToTypeChanged')

    def __init__(self, properties=10, commands=3):
        super(BattleAbilitiesSetupModel, self).__init__(properties=properties, commands=commands)

    @property
    def details(self):
        return self._getViewModel(1)

    @staticmethod
    def getDetailsType():
        return BattleAbilityDetails

    def getIsTypeSelected(self):
        return self._getBool(2)

    def setIsTypeSelected(self, value):
        self._setBool(2, value)

    def getIsCycleFinished(self):
        return self._getBool(3)

    def setIsCycleFinished(self, value):
        self._setBool(3, value)

    def getVehicleType(self):
        return self._getString(4)

    def setVehicleType(self, value):
        self._setString(4, value)

    def getPointsAmount(self):
        return self._getNumber(5)

    def setPointsAmount(self, value):
        self._setNumber(5, value)

    def getTotalPurchasePrice(self):
        return self._getNumber(6)

    def setTotalPurchasePrice(self, value):
        self._setNumber(6, value)

    def getCategoriesOrder(self):
        return self._getArray(7)

    def setCategoriesOrder(self, value):
        self._setArray(7, value)

    @staticmethod
    def getCategoriesOrderType():
        return unicode

    def getKeyNames(self):
        return self._getArray(8)

    def setKeyNames(self, value):
        self._setArray(8, value)

    @staticmethod
    def getKeyNamesType():
        return unicode

    def getSlots(self):
        return self._getArray(9)

    def setSlots(self, value):
        self._setArray(9, value)

    @staticmethod
    def getSlotsType():
        return BattleAbilitySlotModel

    def _initialize(self):
        super(BattleAbilitiesSetupModel, self)._initialize()
        self._addViewModelProperty('details', BattleAbilityDetails())
        self._addBoolProperty('isTypeSelected', False)
        self._addBoolProperty('isCycleFinished', False)
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('pointsAmount', 0)
        self._addNumberProperty('totalPurchasePrice', 0)
        self._addArrayProperty('categoriesOrder', Array())
        self._addArrayProperty('keyNames', Array())
        self._addArrayProperty('slots', Array())
        self.onCurrentAbilityLevelChanged = self._addCommand('onCurrentAbilityLevelChanged')
        self.onApplyToTypeChanged = self._addCommand('onApplyToTypeChanged')
