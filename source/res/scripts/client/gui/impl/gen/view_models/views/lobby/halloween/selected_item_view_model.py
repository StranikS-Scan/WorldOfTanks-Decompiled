# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/halloween/selected_item_view_model.py
from gui.impl.gen.view_models.views.lobby.halloween.base_customization_item_view_model import BaseCustomizationItemViewModel

class SelectedItemViewModel(BaseCustomizationItemViewModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(SelectedItemViewModel, self).__init__(properties=properties, commands=commands)

    def getLongName(self):
        return self._getString(6)

    def setLongName(self, value):
        self._setString(6, value)

    def getDescription(self):
        return self._getString(7)

    def setDescription(self, value):
        self._setString(7, value)

    def getCard(self):
        return self._getString(8)

    def setCard(self, value):
        self._setString(8, value)

    def getVehicleName(self):
        return self._getString(9)

    def setVehicleName(self, value):
        self._setString(9, value)

    def getVehicleType(self):
        return self._getString(10)

    def setVehicleType(self, value):
        self._setString(10, value)

    def getMode(self):
        return self._getString(11)

    def setMode(self, value):
        self._setString(11, value)

    def getBonus(self):
        return self._getString(12)

    def setBonus(self, value):
        self._setString(12, value)

    def getHasVehicleInHangar(self):
        return self._getBool(13)

    def setHasVehicleInHangar(self, value):
        self._setBool(13, value)

    def getIsInBattle(self):
        return self._getBool(14)

    def setIsInBattle(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(SelectedItemViewModel, self)._initialize()
        self._addStringProperty('longName', '')
        self._addStringProperty('description', '')
        self._addStringProperty('card', '')
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('mode', '')
        self._addStringProperty('bonus', '')
        self._addBoolProperty('hasVehicleInHangar', False)
        self._addBoolProperty('isInBattle', False)
