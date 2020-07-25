# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/exchange_dialog_state.py
from frameworks.wulf import ViewModel

class ExchangeDialogState(ViewModel):
    __slots__ = ()
    DEFAULT = 'default'
    NOT_POSSIBLE = 'notPossible'
    NOT_REQUIRED = 'notRequired'

    def __init__(self, properties=0, commands=0):
        super(ExchangeDialogState, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ExchangeDialogState, self)._initialize()
