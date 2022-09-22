# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/tooltips/tooltip_efficiency_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.postbattle.enemy_with_one_param_model import EnemyWithOneParamModel
from gui.impl.gen.view_models.views.lobby.postbattle.simple_efficiency_model import SimpleEfficiencyModel

class TooltipEfficiencyModel(SimpleEfficiencyModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(TooltipEfficiencyModel, self).__init__(properties=properties, commands=commands)

    def getEnemies(self):
        return self._getArray(2)

    def setEnemies(self, value):
        self._setArray(2, value)

    @staticmethod
    def getEnemiesType():
        return EnemyWithOneParamModel

    def _initialize(self):
        super(TooltipEfficiencyModel, self)._initialize()
        self._addArrayProperty('enemies', Array())
