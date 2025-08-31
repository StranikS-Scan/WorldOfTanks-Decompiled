# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crystals_promo/crystals_promo_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.crystals_promo.battle_type_model import BattleTypeModel

class CrystalsPromoViewModel(ViewModel):
    __slots__ = ('goToShop',)
    TANKS_TAB = 'tanksTab'
    INSTRUCTIONS_TAB = 'instructionsTab'
    EQUIPMENT_TAB = 'equipmentTab'
    COMP7_TAB = 'comp7Tab'

    def __init__(self, properties=8, commands=1):
        super(CrystalsPromoViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def battleTypes(self):
        return self._getViewModel(0)

    @staticmethod
    def getBattleTypesType():
        return BattleTypeModel

    def getSelectedTab(self):
        return self._getNumber(1)

    def setSelectedTab(self, value):
        self._setNumber(1, value)

    def getInstructionPrice(self):
        return self._getString(2)

    def setInstructionPrice(self, value):
        self._setString(2, value)

    def getVehiclePrice(self):
        return self._getString(3)

    def setVehiclePrice(self, value):
        self._setString(3, value)

    def getEquipmentPrice(self):
        return self._getString(4)

    def setEquipmentPrice(self, value):
        self._setString(4, value)

    def getComp7Price(self):
        return self._getString(5)

    def setComp7Price(self, value):
        self._setString(5, value)

    def getSyncInitiator(self):
        return self._getBool(6)

    def setSyncInitiator(self, value):
        self._setBool(6, value)

    def getIsChina(self):
        return self._getBool(7)

    def setIsChina(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(CrystalsPromoViewModel, self)._initialize()
        self._addViewModelProperty('battleTypes', UserListModel())
        self._addNumberProperty('selectedTab', 0)
        self._addStringProperty('instructionPrice', '')
        self._addStringProperty('vehiclePrice', '')
        self._addStringProperty('equipmentPrice', '')
        self._addStringProperty('comp7Price', '')
        self._addBoolProperty('syncInitiator', False)
        self._addBoolProperty('isChina', False)
        self.goToShop = self._addCommand('goToShop')
