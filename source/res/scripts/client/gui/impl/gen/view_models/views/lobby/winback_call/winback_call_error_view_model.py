# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback_call/winback_call_error_view_model.py
from frameworks.wulf import ViewModel

class WinbackCallErrorViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=0, commands=1):
        super(WinbackCallErrorViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(WinbackCallErrorViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
