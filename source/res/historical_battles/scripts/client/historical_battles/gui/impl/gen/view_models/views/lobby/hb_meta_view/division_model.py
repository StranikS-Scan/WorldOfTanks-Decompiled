# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_meta_view/division_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.division_level_model import DivisionLevelModel

class DivisionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DivisionModel, self).__init__(properties=properties, commands=commands)

    def getDivisionID(self):
        return self._getNumber(0)

    def setDivisionID(self, value):
        self._setNumber(0, value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getExperience(self):
        return self._getNumber(2)

    def setExperience(self, value):
        self._setNumber(2, value)

    def getLevels(self):
        return self._getArray(3)

    def setLevels(self, value):
        self._setArray(3, value)

    @staticmethod
    def getLevelsType():
        return DivisionLevelModel

    def _initialize(self):
        super(DivisionModel, self)._initialize()
        self._addNumberProperty('divisionID', 0)
        self._addNumberProperty('level', 0)
        self._addNumberProperty('experience', 0)
        self._addArrayProperty('levels', Array())
