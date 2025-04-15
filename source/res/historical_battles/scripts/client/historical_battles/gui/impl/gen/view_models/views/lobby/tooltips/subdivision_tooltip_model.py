# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/subdivision_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.tankset_item_model import TanksetItemModel

class SubdivisionTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(SubdivisionTooltipModel, self).__init__(properties=properties, commands=commands)

    def getFrontName(self):
        return self._getString(0)

    def setFrontName(self, value):
        self._setString(0, value)

    def getSubdivisionID(self):
        return self._getNumber(1)

    def setSubdivisionID(self, value):
        self._setNumber(1, value)

    def getExperience(self):
        return self._getNumber(2)

    def setExperience(self, value):
        self._setNumber(2, value)

    def getMaxExperience(self):
        return self._getNumber(3)

    def setMaxExperience(self, value):
        self._setNumber(3, value)

    def getLevel(self):
        return self._getNumber(4)

    def setLevel(self, value):
        self._setNumber(4, value)

    def getTankSet(self):
        return self._getArray(5)

    def setTankSet(self, value):
        self._setArray(5, value)

    @staticmethod
    def getTankSetType():
        return TanksetItemModel

    def _initialize(self):
        super(SubdivisionTooltipModel, self)._initialize()
        self._addStringProperty('frontName', '')
        self._addNumberProperty('subdivisionID', 0)
        self._addNumberProperty('experience', 0)
        self._addNumberProperty('maxExperience', 0)
        self._addNumberProperty('level', 0)
        self._addArrayProperty('tankSet', Array())
