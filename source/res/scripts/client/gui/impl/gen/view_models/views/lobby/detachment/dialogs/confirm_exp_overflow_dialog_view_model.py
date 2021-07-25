# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/confirm_exp_overflow_dialog_view_model.py
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class ConfirmExpOverflowDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ('onStepperChange',)

    def __init__(self, properties=12, commands=4):
        super(ConfirmExpOverflowDialogViewModel, self).__init__(properties=properties, commands=commands)

    def getAmount(self):
        return self._getNumber(11)

    def setAmount(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(ConfirmExpOverflowDialogViewModel, self)._initialize()
        self._addNumberProperty('amount', 0)
        self.onStepperChange = self._addCommand('onStepperChange')
