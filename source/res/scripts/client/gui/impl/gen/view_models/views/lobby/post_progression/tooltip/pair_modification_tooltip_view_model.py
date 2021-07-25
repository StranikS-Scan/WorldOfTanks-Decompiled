# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/tooltip/pair_modification_tooltip_view_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.bonuses_model import BonusesModel
from gui.impl.gen.view_models.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.post_progression.tooltip.modification_model import ModificationModel

class PairModificationState(Enum):
    UNLOCKED = 'unlocked'
    LOCKED = 'locked'
    BOUGHT = 'bought'
    ANOTHERISINSTALLED = 'anotherIsInstalled'


class PairModificationTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(PairModificationTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @property
    def moneyShortage(self):
        return self._getViewModel(1)

    @property
    def modifiers(self):
        return self._getViewModel(2)

    def getNameRes(self):
        return self._getResource(3)

    def setNameRes(self, value):
        self._setResource(3, value)

    def getLevel(self):
        return self._getNumber(4)

    def setLevel(self, value):
        self._setNumber(4, value)

    def getIsPriceExist(self):
        return self._getBool(5)

    def setIsPriceExist(self, value):
        self._setBool(5, value)

    def getShowCTABlock(self):
        return self._getBool(6)

    def setShowCTABlock(self, value):
        self._setBool(6, value)

    def getState(self):
        return PairModificationState(self._getString(7))

    def setState(self, value):
        self._setString(7, value.value)

    def getModifications(self):
        return self._getArray(8)

    def setModifications(self, value):
        self._setArray(8, value)

    def _initialize(self):
        super(PairModificationTooltipViewModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addViewModelProperty('moneyShortage', PriceModel())
        self._addViewModelProperty('modifiers', BonusesModel())
        self._addResourceProperty('nameRes', R.invalid())
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isPriceExist', True)
        self._addBoolProperty('showCTABlock', True)
        self._addStringProperty('state')
        self._addArrayProperty('modifications', Array())
