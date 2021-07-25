# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/apply_exp_exchange_dialog_view_model.py
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class ApplyExpExchangeDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=3):
        super(ApplyExpExchangeDialogViewModel, self).__init__(properties=properties, commands=commands)

    def getFreeExp(self):
        return self._getNumber(11)

    def setFreeExp(self, value):
        self._setNumber(11, value)

    def getRate(self):
        return self._getNumber(12)

    def setRate(self, value):
        self._setNumber(12, value)

    def getIsExchangeDiscount(self):
        return self._getBool(13)

    def setIsExchangeDiscount(self, value):
        self._setBool(13, value)

    def getIsMaxLevel(self):
        return self._getBool(14)

    def setIsMaxLevel(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(ApplyExpExchangeDialogViewModel, self)._initialize()
        self._addNumberProperty('freeExp', 0)
        self._addNumberProperty('rate', 0)
        self._addBoolProperty('isExchangeDiscount', False)
        self._addBoolProperty('isMaxLevel', False)
