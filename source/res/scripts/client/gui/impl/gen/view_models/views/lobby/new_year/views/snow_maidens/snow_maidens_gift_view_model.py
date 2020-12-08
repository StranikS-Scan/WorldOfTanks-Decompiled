# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/snow_maidens/snow_maidens_gift_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class SnowMaidensGiftViewModel(ViewModel):
    __slots__ = ('onClose', 'onBackToTree', 'onTakeGift')

    def __init__(self, properties=6, commands=3):
        super(SnowMaidensGiftViewModel, self).__init__(properties=properties, commands=commands)

    def getDialogType(self):
        return self._getString(0)

    def setDialogType(self, value):
        self._setString(0, value)

    def getSnowMaidenType(self):
        return self._getString(1)

    def setSnowMaidenType(self, value):
        self._setString(1, value)

    def getSnowMaidensAmount(self):
        return self._getNumber(2)

    def setSnowMaidensAmount(self, value):
        self._setNumber(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    def getCooldown(self):
        return self._getNumber(4)

    def setCooldown(self, value):
        self._setNumber(4, value)

    def getProgressLevel(self):
        return self._getNumber(5)

    def setProgressLevel(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(SnowMaidensGiftViewModel, self)._initialize()
        self._addStringProperty('dialogType', '')
        self._addStringProperty('snowMaidenType', '')
        self._addNumberProperty('snowMaidensAmount', 0)
        self._addArrayProperty('rewards', Array())
        self._addNumberProperty('cooldown', -1)
        self._addNumberProperty('progressLevel', 0)
        self.onClose = self._addCommand('onClose')
        self.onBackToTree = self._addCommand('onBackToTree')
        self.onTakeGift = self._addCommand('onTakeGift')
