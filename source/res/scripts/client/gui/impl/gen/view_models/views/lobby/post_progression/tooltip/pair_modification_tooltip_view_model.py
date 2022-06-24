# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/tooltip/pair_modification_tooltip_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.bonuses_model import BonusesModel
from gui.impl.gen.view_models.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.post_progression.multi_step_model import MultiStepModel

class PairModificationTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(PairModificationTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceModel

    @property
    def moneyShortage(self):
        return self._getViewModel(1)

    @staticmethod
    def getMoneyShortageType():
        return PriceModel

    @property
    def modifiers(self):
        return self._getViewModel(2)

    @staticmethod
    def getModifiersType():
        return BonusesModel

    @property
    def multiStep(self):
        return self._getViewModel(3)

    @staticmethod
    def getMultiStepType():
        return MultiStepModel

    def getNameRes(self):
        return self._getResource(4)

    def setNameRes(self, value):
        self._setResource(4, value)

    def getLevel(self):
        return self._getNumber(5)

    def setLevel(self, value):
        self._setNumber(5, value)

    def getIsPriceExist(self):
        return self._getBool(6)

    def setIsPriceExist(self, value):
        self._setBool(6, value)

    def getShowCTABlock(self):
        return self._getBool(7)

    def setShowCTABlock(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(PairModificationTooltipViewModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addViewModelProperty('moneyShortage', PriceModel())
        self._addViewModelProperty('modifiers', BonusesModel())
        self._addViewModelProperty('multiStep', MultiStepModel())
        self._addResourceProperty('nameRes', R.invalid())
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isPriceExist', True)
        self._addBoolProperty('showCTABlock', True)
