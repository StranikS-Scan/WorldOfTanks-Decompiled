# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/frontline_setup_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_ability_details import BattleAbilityDetails
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_ability_slot_model import BattleAbilitySlotModel

class FrontlineSetupModel(BaseSetupModel):
    __slots__ = ('showInfoPage', 'purchaseSelectedAbilities', 'setCurrentSlotDetailsLevel', 'onChangeApplyAbilitiesToTypeSettings')

    def __init__(self, properties=13, commands=11):
        super(FrontlineSetupModel, self).__init__(properties=properties, commands=commands)

    @property
    def details(self):
        return self._getViewModel(5)

    @staticmethod
    def getDetailsType():
        return BattleAbilityDetails

    def getIsLocked(self):
        return self._getBool(6)

    def setIsLocked(self, value):
        self._setBool(6, value)

    def getIsTypeSelected(self):
        return self._getBool(7)

    def setIsTypeSelected(self, value):
        self._setBool(7, value)

    def getVehicleType(self):
        return self._getString(8)

    def setVehicleType(self, value):
        self._setString(8, value)

    def getPointsAmount(self):
        return self._getNumber(9)

    def setPointsAmount(self, value):
        self._setNumber(9, value)

    def getTotalPurchasePrice(self):
        return self._getNumber(10)

    def setTotalPurchasePrice(self, value):
        self._setNumber(10, value)

    def getCategoriesOrder(self):
        return self._getArray(11)

    def setCategoriesOrder(self, value):
        self._setArray(11, value)

    @staticmethod
    def getCategoriesOrderType():
        return unicode

    def getSlots(self):
        return self._getArray(12)

    def setSlots(self, value):
        self._setArray(12, value)

    @staticmethod
    def getSlotsType():
        return BattleAbilitySlotModel

    def _initialize(self):
        super(FrontlineSetupModel, self)._initialize()
        self._addViewModelProperty('details', BattleAbilityDetails())
        self._addBoolProperty('isLocked', True)
        self._addBoolProperty('isTypeSelected', False)
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('pointsAmount', 0)
        self._addNumberProperty('totalPurchasePrice', 0)
        self._addArrayProperty('categoriesOrder', Array())
        self._addArrayProperty('slots', Array())
        self.showInfoPage = self._addCommand('showInfoPage')
        self.purchaseSelectedAbilities = self._addCommand('purchaseSelectedAbilities')
        self.setCurrentSlotDetailsLevel = self._addCommand('setCurrentSlotDetailsLevel')
        self.onChangeApplyAbilitiesToTypeSettings = self._addCommand('onChangeApplyAbilitiesToTypeSettings')
