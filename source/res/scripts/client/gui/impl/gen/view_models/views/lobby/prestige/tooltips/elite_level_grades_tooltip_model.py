# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/prestige/tooltips/elite_level_grades_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeEmblemModel

class EliteLevelGradesTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(EliteLevelGradesTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCurrentLevel(self):
        return self._getNumber(0)

    def setCurrentLevel(self, value):
        self._setNumber(0, value)

    def getEmblems(self):
        return self._getArray(1)

    def setEmblems(self, value):
        self._setArray(1, value)

    @staticmethod
    def getEmblemsType():
        return PrestigeEmblemModel

    def _initialize(self):
        super(EliteLevelGradesTooltipModel, self)._initialize()
        self._addNumberProperty('currentLevel', 0)
        self._addArrayProperty('emblems', Array())
