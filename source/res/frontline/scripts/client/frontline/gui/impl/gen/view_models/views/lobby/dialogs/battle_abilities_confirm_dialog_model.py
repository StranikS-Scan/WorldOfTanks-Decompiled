# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/dialogs/battle_abilities_confirm_dialog_model.py
from frameworks.wulf import Array, ViewModel

class BattleAbilitiesConfirmDialogModel(ViewModel):
    __slots__ = ('onCheckBoxClick', 'onSubmitClick', 'onCancelClick', 'onCloseClick')

    def __init__(self, properties=10, commands=4):
        super(BattleAbilitiesConfirmDialogModel, self).__init__(properties=properties, commands=commands)

    def getPrice(self):
        return self._getNumber(0)

    def setPrice(self, value):
        self._setNumber(0, value)

    def getBonus(self):
        return self._getNumber(1)

    def setBonus(self, value):
        self._setNumber(1, value)

    def getIsBuy(self):
        return self._getBool(2)

    def setIsBuy(self, value):
        self._setBool(2, value)

    def getIsMultipleAbilities(self):
        return self._getBool(3)

    def setIsMultipleAbilities(self, value):
        self._setBool(3, value)

    def getIsTypeSelected(self):
        return self._getBool(4)

    def setIsTypeSelected(self, value):
        self._setBool(4, value)

    def getIsEnoughMoney(self):
        return self._getBool(5)

    def setIsEnoughMoney(self, value):
        self._setBool(5, value)

    def getSelectedSkillName(self):
        return self._getString(6)

    def setSelectedSkillName(self, value):
        self._setString(6, value)

    def getVehicleType(self):
        return self._getString(7)

    def setVehicleType(self, value):
        self._setString(7, value)

    def getIcons(self):
        return self._getArray(8)

    def setIcons(self, value):
        self._setArray(8, value)

    @staticmethod
    def getIconsType():
        return unicode

    def getNames(self):
        return self._getArray(9)

    def setNames(self, value):
        self._setArray(9, value)

    @staticmethod
    def getNamesType():
        return unicode

    def _initialize(self):
        super(BattleAbilitiesConfirmDialogModel, self)._initialize()
        self._addNumberProperty('price', 0)
        self._addNumberProperty('bonus', 0)
        self._addBoolProperty('isBuy', False)
        self._addBoolProperty('isMultipleAbilities', False)
        self._addBoolProperty('isTypeSelected', False)
        self._addBoolProperty('isEnoughMoney', False)
        self._addStringProperty('selectedSkillName', '')
        self._addStringProperty('vehicleType', '')
        self._addArrayProperty('icons', Array())
        self._addArrayProperty('names', Array())
        self.onCheckBoxClick = self._addCommand('onCheckBoxClick')
        self.onSubmitClick = self._addCommand('onSubmitClick')
        self.onCancelClick = self._addCommand('onCancelClick')
        self.onCloseClick = self._addCommand('onCloseClick')
