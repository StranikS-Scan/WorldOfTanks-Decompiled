# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/envelopes_popover_model.py
from frameworks.wulf import ViewModel

class EnvelopesPopoverModel(ViewModel):
    __slots__ = ('onQuestsClick', 'onSendClick', 'onBuyClick')

    def __init__(self, properties=7, commands=3):
        super(EnvelopesPopoverModel, self).__init__(properties=properties, commands=commands)

    def getGiftSystemIsEnabled(self):
        return self._getBool(0)

    def setGiftSystemIsEnabled(self, value):
        self._setBool(0, value)

    def getFreeIsEnabled(self):
        return self._getBool(1)

    def setFreeIsEnabled(self, value):
        self._setBool(1, value)

    def getPaidIsEnabled(self):
        return self._getBool(2)

    def setPaidIsEnabled(self, value):
        self._setBool(2, value)

    def getPremiumIsEnabled(self):
        return self._getBool(3)

    def setPremiumIsEnabled(self, value):
        self._setBool(3, value)

    def getFreeCount(self):
        return self._getNumber(4)

    def setFreeCount(self, value):
        self._setNumber(4, value)

    def getPaidCount(self):
        return self._getNumber(5)

    def setPaidCount(self, value):
        self._setNumber(5, value)

    def getPremiumCount(self):
        return self._getNumber(6)

    def setPremiumCount(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(EnvelopesPopoverModel, self)._initialize()
        self._addBoolProperty('giftSystemIsEnabled', False)
        self._addBoolProperty('freeIsEnabled', False)
        self._addBoolProperty('paidIsEnabled', False)
        self._addBoolProperty('premiumIsEnabled', False)
        self._addNumberProperty('freeCount', 0)
        self._addNumberProperty('paidCount', 0)
        self._addNumberProperty('premiumCount', 0)
        self.onQuestsClick = self._addCommand('onQuestsClick')
        self.onSendClick = self._addCommand('onSendClick')
        self.onBuyClick = self._addCommand('onBuyClick')
