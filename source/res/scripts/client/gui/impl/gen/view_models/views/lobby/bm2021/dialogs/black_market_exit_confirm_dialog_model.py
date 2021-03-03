# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bm2021/dialogs/black_market_exit_confirm_dialog_model.py
from frameworks.wulf import ViewModel

class BlackMarketExitConfirmDialogModel(ViewModel):
    __slots__ = ('onConfirm',)

    def __init__(self, properties=1, commands=1):
        super(BlackMarketExitConfirmDialogModel, self).__init__(properties=properties, commands=commands)

    def getEndDate(self):
        return self._getNumber(0)

    def setEndDate(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(BlackMarketExitConfirmDialogModel, self)._initialize()
        self._addNumberProperty('endDate', 0)
        self.onConfirm = self._addCommand('onConfirm')
