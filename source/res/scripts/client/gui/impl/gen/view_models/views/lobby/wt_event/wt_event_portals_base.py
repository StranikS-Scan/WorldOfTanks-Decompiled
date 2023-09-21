# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_portals_base.py
from frameworks.wulf import ViewModel

class WtEventPortalsBase(ViewModel):
    __slots__ = ('onBuyButtonClick', 'onClose')

    def __init__(self, properties=2, commands=2):
        super(WtEventPortalsBase, self).__init__(properties=properties, commands=commands)

    def getIsBoxesEnabled(self):
        return self._getBool(0)

    def setIsBoxesEnabled(self, value):
        self._setBool(0, value)

    def getAvailableLootBoxesPurchase(self):
        return self._getNumber(1)

    def setAvailableLootBoxesPurchase(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(WtEventPortalsBase, self)._initialize()
        self._addBoolProperty('isBoxesEnabled', True)
        self._addNumberProperty('availableLootBoxesPurchase', -1)
        self.onBuyButtonClick = self._addCommand('onBuyButtonClick')
        self.onClose = self._addCommand('onClose')
