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

    def __init__(self, properties=6, commands=0):
        super(PairModificationTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @property
    def modifiers(self):
        return self._getViewModel(1)

    def getNameRes(self):
        return self._getResource(2)

    def setNameRes(self, value):
        self._setResource(2, value)

    def getLevel(self):
        return self._getNumber(3)

    def setLevel(self, value):
        self._setNumber(3, value)

    def getState(self):
        return PairModificationState(self._getString(4))

    def setState(self, value):
        self._setString(4, value.value)

    def getModifications(self):
        return self._getArray(5)

    def setModifications(self, value):
        self._setArray(5, value)

    def _initialize(self):
        super(PairModificationTooltipViewModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addViewModelProperty('modifiers', BonusesModel())
        self._addResourceProperty('nameRes', R.invalid())
        self._addNumberProperty('level', 0)
        self._addStringProperty('state')
        self._addArrayProperty('modifications', Array())
