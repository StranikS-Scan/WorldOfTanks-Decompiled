# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/enemy_multi_params_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.postbattle.efficiency_item_model import EfficiencyItemModel
from gui.impl.gen.view_models.views.lobby.postbattle.enemy_base_model import EnemyBaseModel

class EnemyMultiParamsModel(EnemyBaseModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(EnemyMultiParamsModel, self).__init__(properties=properties, commands=commands)

    def getParams(self):
        return self._getArray(9)

    def setParams(self, value):
        self._setArray(9, value)

    def _initialize(self):
        super(EnemyMultiParamsModel, self)._initialize()
        self._addArrayProperty('params', Array())
