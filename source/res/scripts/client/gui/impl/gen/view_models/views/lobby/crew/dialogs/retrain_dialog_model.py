# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/retrain_dialog_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.retrain_tankman_model import RetrainTankmanModel

class RetrainDialogModel(DialogTemplateViewModel):
    __slots__ = ('onTransferChanged',)

    def __init__(self, properties=13, commands=3):
        super(RetrainDialogModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(6)

    def setVehicleName(self, value):
        self._setString(6, value)

    def getIsPremium(self):
        return self._getBool(7)

    def setIsPremium(self, value):
        self._setBool(7, value)

    def getIsPriceVisible(self):
        return self._getBool(8)

    def setIsPriceVisible(self, value):
        self._setBool(8, value)

    def getIsTransferSelectionVisible(self):
        return self._getBool(9)

    def setIsTransferSelectionVisible(self, value):
        self._setBool(9, value)

    def getIsTransferChecked(self):
        return self._getBool(10)

    def setIsTransferChecked(self, value):
        self._setBool(10, value)

    def getIsMassive(self):
        return self._getBool(11)

    def setIsMassive(self, value):
        self._setBool(11, value)

    def getTankmen(self):
        return self._getArray(12)

    def setTankmen(self, value):
        self._setArray(12, value)

    @staticmethod
    def getTankmenType():
        return RetrainTankmanModel

    def _initialize(self):
        super(RetrainDialogModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addBoolProperty('isPremium', False)
        self._addBoolProperty('isPriceVisible', False)
        self._addBoolProperty('isTransferSelectionVisible', False)
        self._addBoolProperty('isTransferChecked', True)
        self._addBoolProperty('isMassive', False)
        self._addArrayProperty('tankmen', Array())
        self.onTransferChanged = self._addCommand('onTransferChanged')
