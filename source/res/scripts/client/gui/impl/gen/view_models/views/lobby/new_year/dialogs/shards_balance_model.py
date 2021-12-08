# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/shards_balance_model.py
from frameworks.wulf import ViewModel

class ShardsBalanceModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ShardsBalanceModel, self).__init__(properties=properties, commands=commands)

    def getBalance(self):
        return self._getNumber(0)

    def setBalance(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(ShardsBalanceModel, self)._initialize()
        self._addNumberProperty('balance', 0)
