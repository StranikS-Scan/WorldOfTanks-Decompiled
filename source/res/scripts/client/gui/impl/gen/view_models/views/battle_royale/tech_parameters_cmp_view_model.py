# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/tech_parameters_cmp_view_model.py
from frameworks.wulf import ViewModel

class TechParametersCmpViewModel(ViewModel):
    __slots__ = ('onClick', 'onResized')

    def __init__(self, properties=5, commands=2):
        super(TechParametersCmpViewModel, self).__init__(properties=properties, commands=commands)

    def getDifficulty(self):
        return self._getNumber(0)

    def setDifficulty(self, value):
        self._setNumber(0, value)

    def getSpotting(self):
        return self._getNumber(1)

    def setSpotting(self, value):
        self._setNumber(1, value)

    def getMobility(self):
        return self._getNumber(2)

    def setMobility(self, value):
        self._setNumber(2, value)

    def getSurvivability(self):
        return self._getNumber(3)

    def setSurvivability(self, value):
        self._setNumber(3, value)

    def getDamage(self):
        return self._getNumber(4)

    def setDamage(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(TechParametersCmpViewModel, self)._initialize()
        self._addNumberProperty('difficulty', 0)
        self._addNumberProperty('spotting', 0)
        self._addNumberProperty('mobility', 0)
        self._addNumberProperty('survivability', 0)
        self._addNumberProperty('damage', 0)
        self.onClick = self._addCommand('onClick')
        self.onResized = self._addCommand('onResized')
