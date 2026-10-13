# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/dialogs/hw_dialog_model.py
from frameworks.wulf import ViewModel

class HwDialogModel(ViewModel):
    __slots__ = ('onSubmitClick', 'onCancelClick', 'onCloseClick')

    def __init__(self, properties=0, commands=3):
        super(HwDialogModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(HwDialogModel, self)._initialize()
        self.onSubmitClick = self._addCommand('onSubmitClick')
        self.onCancelClick = self._addCommand('onCancelClick')
        self.onCloseClick = self._addCommand('onCloseClick')
