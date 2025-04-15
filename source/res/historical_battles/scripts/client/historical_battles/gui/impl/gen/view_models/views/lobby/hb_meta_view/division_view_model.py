# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_meta_view/division_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.division_model import DivisionModel

class DivisionViewModel(ViewModel):
    __slots__ = ('onBuyLevel',)

    def __init__(self, properties=2, commands=1):
        super(DivisionViewModel, self).__init__(properties=properties, commands=commands)

    def getFrontName(self):
        return self._getString(0)

    def setFrontName(self, value):
        self._setString(0, value)

    def getDivisions(self):
        return self._getArray(1)

    def setDivisions(self, value):
        self._setArray(1, value)

    @staticmethod
    def getDivisionsType():
        return DivisionModel

    def _initialize(self):
        super(DivisionViewModel, self)._initialize()
        self._addStringProperty('frontName', '')
        self._addArrayProperty('divisions', Array())
        self.onBuyLevel = self._addCommand('onBuyLevel')
