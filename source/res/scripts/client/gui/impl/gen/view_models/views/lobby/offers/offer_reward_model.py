# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/offers/offer_reward_model.py
from frameworks.wulf import ViewModel

class OfferRewardModel(ViewModel):
    __slots__ = ('onClose', 'onAccept')

    def __init__(self, properties=7, commands=2):
        super(OfferRewardModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getTooltipTitle(self):
        return self._getString(2)

    def setTooltipTitle(self, value):
        self._setString(2, value)

    def getTooltipDescription(self):
        return self._getString(3)

    def setTooltipDescription(self, value):
        self._setString(3, value)

    def getCount(self):
        return self._getNumber(4)

    def setCount(self, value):
        self._setNumber(4, value)

    def getBonusType(self):
        return self._getString(5)

    def setBonusType(self, value):
        self._setString(5, value)

    def getHightlightType(self):
        return self._getString(6)

    def setHightlightType(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(OfferRewardModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('tooltipTitle', '')
        self._addStringProperty('tooltipDescription', '')
        self._addNumberProperty('count', 0)
        self._addStringProperty('bonusType', '')
        self._addStringProperty('hightlightType', '')
        self.onClose = self._addCommand('onClose')
        self.onAccept = self._addCommand('onAccept')
