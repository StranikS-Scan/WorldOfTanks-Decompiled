# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback/winback_leave_mode_dialog_view_model.py
from frameworks.wulf import ViewModel

class WinbackLeaveModeDialogViewModel(ViewModel):
    __slots__ = ('onClose', 'onLeaveMode')

    def __init__(self, properties=0, commands=2):
        super(WinbackLeaveModeDialogViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(WinbackLeaveModeDialogViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
        self.onLeaveMode = self._addCommand('onLeaveMode')
