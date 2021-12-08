# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_mega_decoration_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NyMegaDecorationTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(NyMegaDecorationTooltipModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getResource(0)

    def setName(self, value):
        self._setResource(0, value)

    def getDescription(self):
        return self._getResource(1)

    def setDescription(self, value):
        self._setResource(1, value)

    def getShardsPrice(self):
        return self._getNumber(2)

    def setShardsPrice(self, value):
        self._setNumber(2, value)

    def getBonus(self):
        return self._getReal(3)

    def setBonus(self, value):
        self._setReal(3, value)

    def getIcon(self):
        return self._getResource(4)

    def setIcon(self, value):
        self._setResource(4, value)

    def getIsPure(self):
        return self._getBool(5)

    def setIsPure(self, value):
        self._setBool(5, value)

    def getPureSlotAtmosphere(self):
        return self._getNumber(6)

    def setPureSlotAtmosphere(self, value):
        self._setNumber(6, value)

    def getIsMaxAtmosphereLevel(self):
        return self._getBool(7)

    def setIsMaxAtmosphereLevel(self, value):
        self._setBool(7, value)

    def getIsPostNYEnabled(self):
        return self._getBool(8)

    def setIsPostNYEnabled(self, value):
        self._setBool(8, value)

    def getIsFinished(self):
        return self._getBool(9)

    def setIsFinished(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(NyMegaDecorationTooltipModel, self)._initialize()
        self._addResourceProperty('name', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addNumberProperty('shardsPrice', 0)
        self._addRealProperty('bonus', 0.0)
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isPure', False)
        self._addNumberProperty('pureSlotAtmosphere', 0)
        self._addBoolProperty('isMaxAtmosphereLevel', False)
        self._addBoolProperty('isPostNYEnabled', False)
        self._addBoolProperty('isFinished', False)
