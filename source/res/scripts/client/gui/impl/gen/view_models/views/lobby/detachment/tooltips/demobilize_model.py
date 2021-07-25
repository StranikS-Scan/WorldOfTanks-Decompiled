# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/demobilize_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel

class DemobilizeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(DemobilizeModel, self).__init__(properties=properties, commands=commands)

    @property
    def priceModel(self):
        return self._getViewModel(0)

    def getFullTerm(self):
        return self._getNumber(1)

    def setFullTerm(self, value):
        self._setNumber(1, value)

    def getFreeTerm(self):
        return self._getNumber(2)

    def setFreeTerm(self, value):
        self._setNumber(2, value)

    def getPaidTerm(self):
        return self._getNumber(3)

    def setPaidTerm(self, value):
        self._setNumber(3, value)

    def getDissolvedCount(self):
        return self._getNumber(4)

    def setDissolvedCount(self, value):
        self._setNumber(4, value)

    def getRecycleMax(self):
        return self._getNumber(5)

    def setRecycleMax(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(DemobilizeModel, self)._initialize()
        self._addViewModelProperty('priceModel', PriceModel())
        self._addNumberProperty('fullTerm', 0)
        self._addNumberProperty('freeTerm', 0)
        self._addNumberProperty('paidTerm', 0)
        self._addNumberProperty('dissolvedCount', 0)
        self._addNumberProperty('recycleMax', 0)
