# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/gen/view_models/views/lobby/cell_model.py
from frameworks.wulf import Array, ViewModel
from open_bundle.gui.impl.gen.view_models.views.lobby.bonus_model import BonusModel
from open_bundle.gui.impl.gen.view_models.views.lobby.coordinates_model import CoordinatesModel

class CellModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(CellModel, self).__init__(properties=properties, commands=commands)

    @property
    def coordinates(self):
        return self._getViewModel(0)

    @staticmethod
    def getCoordinatesType():
        return CoordinatesModel

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getProbability(self):
        return self._getReal(2)

    def setProbability(self, value):
        self._setReal(2, value)

    def getIsRare(self):
        return self._getBool(3)

    def setIsRare(self, value):
        self._setBool(3, value)

    def getTemplate(self):
        return self._getString(4)

    def setTemplate(self, value):
        self._setString(4, value)

    def getState(self):
        return self._getString(5)

    def setState(self, value):
        self._setString(5, value)

    def getBonuses(self):
        return self._getArray(6)

    def setBonuses(self, value):
        self._setArray(6, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(CellModel, self)._initialize()
        self._addViewModelProperty('coordinates', CoordinatesModel())
        self._addStringProperty('name', '')
        self._addRealProperty('probability', 0.0)
        self._addBoolProperty('isRare', False)
        self._addStringProperty('template', '')
        self._addStringProperty('state', '')
        self._addArrayProperty('bonuses', Array())
