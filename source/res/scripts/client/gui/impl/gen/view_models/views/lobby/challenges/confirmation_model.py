# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/challenges/confirmation_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel

class ConfirmationModel(ViewModel):
    __slots__ = ('confirm', 'cancel')

    def __init__(self, properties=7, commands=2):
        super(ConfirmationModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceItemModel

    def getChallengeID(self):
        return self._getNumber(1)

    def setChallengeID(self, value):
        self._setNumber(1, value)

    def getChallengeName(self):
        return self._getString(2)

    def setChallengeName(self, value):
        self._setString(2, value)

    def getConfirmationType(self):
        return self._getString(3)

    def setConfirmationType(self, value):
        self._setString(3, value)

    def getIsFreeRestart(self):
        return self._getBool(4)

    def setIsFreeRestart(self, value):
        self._setBool(4, value)

    def getBalance(self):
        return self._getArray(5)

    def setBalance(self, value):
        self._setArray(5, value)

    @staticmethod
    def getBalanceType():
        return PriceItemModel

    def getIsWalletAvailable(self):
        return self._getBool(6)

    def setIsWalletAvailable(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(ConfirmationModel, self)._initialize()
        self._addViewModelProperty('price', PriceItemModel())
        self._addNumberProperty('challengeID', 0)
        self._addStringProperty('challengeName', '')
        self._addStringProperty('confirmationType', '')
        self._addBoolProperty('isFreeRestart', False)
        self._addArrayProperty('balance', Array())
        self._addBoolProperty('isWalletAvailable', True)
        self.confirm = self._addCommand('confirm')
        self.cancel = self._addCommand('cancel')
