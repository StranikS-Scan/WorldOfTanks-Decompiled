# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/telecom/telecom_view_model.py
from frameworks.wulf import ViewModel

class TelecomViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=0, commands=1):
        super(TelecomViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(TelecomViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
