# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/external_points_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen import R

class ExternalPointsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ExternalPointsModel, self).__init__(properties=properties, commands=commands)

    def getPoints(self):
        return self._getNumber(0)

    def setPoints(self, value):
        self._setNumber(0, value)

    def getLabel(self):
        return self._getResource(1)

    def setLabel(self, value):
        self._setResource(1, value)

    def getIsActive(self):
        return self._getBool(2)

    def setIsActive(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(ExternalPointsModel, self)._initialize()
        self._addNumberProperty('points', 0)
        self._addResourceProperty('label', R.invalid())
        self._addBoolProperty('isActive', False)
