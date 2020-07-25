# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/transfer_giveaway/transfer_giveaway_awards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class TransferGiveawayAwardsViewModel(ViewModel):
    __slots__ = ('onCloseAction',)

    def __init__(self, properties=4, commands=1):
        super(TransferGiveawayAwardsViewModel, self).__init__(properties=properties, commands=commands)

    def getCategory(self):
        return self._getString(0)

    def setCategory(self, value):
        self._setString(0, value)

    def getBonuses(self):
        return self._getArray(1)

    def setBonuses(self, value):
        self._setArray(1, value)

    def getVehicles(self):
        return self._getArray(2)

    def setVehicles(self, value):
        self._setArray(2, value)

    def getBoxCount(self):
        return self._getNumber(3)

    def setBoxCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(TransferGiveawayAwardsViewModel, self)._initialize()
        self._addStringProperty('category', '')
        self._addArrayProperty('bonuses', Array())
        self._addArrayProperty('vehicles', Array())
        self._addNumberProperty('boxCount', 0)
        self.onCloseAction = self._addCommand('onCloseAction')
