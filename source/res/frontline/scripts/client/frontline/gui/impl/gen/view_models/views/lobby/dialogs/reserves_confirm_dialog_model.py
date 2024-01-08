# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/dialogs/reserves_confirm_dialog_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel

class ReservesConfirmDialogModel(DialogTemplateViewModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=2):
        super(ReservesConfirmDialogModel, self).__init__(properties=properties, commands=commands)

    def getPrice(self):
        return self._getNumber(6)

    def setPrice(self, value):
        self._setNumber(6, value)

    def getBonus(self):
        return self._getNumber(7)

    def setBonus(self, value):
        self._setNumber(7, value)

    def getIsBuy(self):
        return self._getBool(8)

    def setIsBuy(self, value):
        self._setBool(8, value)

    def getIsMultipleReserves(self):
        return self._getBool(9)

    def setIsMultipleReserves(self, value):
        self._setBool(9, value)

    def getTitleText(self):
        return self._getString(10)

    def setTitleText(self, value):
        self._setString(10, value)

    def getSelectedSkillName(self):
        return self._getString(11)

    def setSelectedSkillName(self, value):
        self._setString(11, value)

    def getVehicleType(self):
        return self._getString(12)

    def setVehicleType(self, value):
        self._setString(12, value)

    def getIcons(self):
        return self._getArray(13)

    def setIcons(self, value):
        self._setArray(13, value)

    @staticmethod
    def getIconsType():
        return unicode

    def getNames(self):
        return self._getArray(14)

    def setNames(self, value):
        self._setArray(14, value)

    @staticmethod
    def getNamesType():
        return unicode

    def _initialize(self):
        super(ReservesConfirmDialogModel, self)._initialize()
        self._addNumberProperty('price', 0)
        self._addNumberProperty('bonus', 0)
        self._addBoolProperty('isBuy', False)
        self._addBoolProperty('isMultipleReserves', False)
        self._addStringProperty('titleText', '')
        self._addStringProperty('selectedSkillName', '')
        self._addStringProperty('vehicleType', '')
        self._addArrayProperty('icons', Array())
        self._addArrayProperty('names', Array())
