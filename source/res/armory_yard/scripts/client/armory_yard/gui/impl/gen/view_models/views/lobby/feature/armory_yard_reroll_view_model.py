# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_reroll_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_quest_sub_model import ArmoryYardQuestSubModel
from gui.impl.gen.view_models.views.dialogs.sub_views.money_balance_view_model import MoneyBalanceViewModel

class ArmoryYardRerollViewModel(ViewModel):
    __slots__ = ('onReroll', 'onConfirm', 'onClose')

    def __init__(self, properties=14, commands=3):
        super(ArmoryYardRerollViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentQuest(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrentQuestType():
        return ArmoryYardQuestSubModel

    @property
    def price(self):
        return self._getViewModel(1)

    @staticmethod
    def getPriceType():
        return PriceModel

    @property
    def moneyBalance(self):
        return self._getViewModel(2)

    @staticmethod
    def getMoneyBalanceType():
        return MoneyBalanceViewModel

    def getFromTimestamp(self):
        return self._getNumber(3)

    def setFromTimestamp(self, value):
        self._setNumber(3, value)

    def getToTimestamp(self):
        return self._getNumber(4)

    def setToTimestamp(self, value):
        self._setNumber(4, value)

    def getFreeRerollCount(self):
        return self._getNumber(5)

    def setFreeRerollCount(self, value):
        self._setNumber(5, value)

    def getRerollCountdown(self):
        return self._getNumber(6)

    def setRerollCountdown(self, value):
        self._setNumber(6, value)

    def getIsPostProgression(self):
        return self._getBool(7)

    def setIsPostProgression(self, value):
        self._setBool(7, value)

    def getIsPostProgressionQuest(self):
        return self._getBool(8)

    def setIsPostProgressionQuest(self, value):
        self._setBool(8, value)

    def getIsPostProgressionFinished(self):
        return self._getBool(9)

    def setIsPostProgressionFinished(self, value):
        self._setBool(9, value)

    def getCanCloseWindow(self):
        return self._getBool(10)

    def setCanCloseWindow(self, value):
        self._setBool(10, value)

    def getIsPaymentError(self):
        return self._getBool(11)

    def setIsPaymentError(self, value):
        self._setBool(11, value)

    def getIsIntroScreenVisited(self):
        return self._getBool(12)

    def setIsIntroScreenVisited(self, value):
        self._setBool(12, value)

    def getSuggestedQuests(self):
        return self._getArray(13)

    def setSuggestedQuests(self, value):
        self._setArray(13, value)

    @staticmethod
    def getSuggestedQuestsType():
        return ArmoryYardQuestSubModel

    def _initialize(self):
        super(ArmoryYardRerollViewModel, self)._initialize()
        self._addViewModelProperty('currentQuest', ArmoryYardQuestSubModel())
        self._addViewModelProperty('price', PriceModel())
        self._addViewModelProperty('moneyBalance', MoneyBalanceViewModel())
        self._addNumberProperty('fromTimestamp', 0)
        self._addNumberProperty('toTimestamp', 0)
        self._addNumberProperty('freeRerollCount', 0)
        self._addNumberProperty('rerollCountdown', 0)
        self._addBoolProperty('isPostProgression', False)
        self._addBoolProperty('isPostProgressionQuest', False)
        self._addBoolProperty('isPostProgressionFinished', False)
        self._addBoolProperty('canCloseWindow', True)
        self._addBoolProperty('isPaymentError', False)
        self._addBoolProperty('isIntroScreenVisited', True)
        self._addArrayProperty('suggestedQuests', Array())
        self.onReroll = self._addCommand('onReroll')
        self.onConfirm = self._addCommand('onConfirm')
        self.onClose = self._addCommand('onClose')
