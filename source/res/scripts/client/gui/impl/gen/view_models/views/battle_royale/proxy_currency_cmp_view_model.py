# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/proxy_currency_cmp_view_model.py
from frameworks.wulf import ViewModel

class ProxyCurrencyCmpViewModel(ViewModel):
    __slots__ = ('onGotoShopBtnClicked',)

    def __init__(self, properties=1, commands=1):
        super(ProxyCurrencyCmpViewModel, self).__init__(properties=properties, commands=commands)

    def getBalance(self):
        return self._getNumber(0)

    def setBalance(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(ProxyCurrencyCmpViewModel, self)._initialize()
        self._addNumberProperty('balance', 0)
        self.onGotoShopBtnClicked = self._addCommand('onGotoShopBtnClicked')
