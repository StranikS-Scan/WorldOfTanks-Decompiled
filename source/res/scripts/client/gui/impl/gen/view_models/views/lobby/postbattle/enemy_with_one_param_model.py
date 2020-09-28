# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/enemy_with_one_param_model.py
from gui.impl.gen.view_models.views.lobby.postbattle.enemy_base_model import EnemyBaseModel

class EnemyWithOneParamModel(EnemyBaseModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(EnemyWithOneParamModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getNumber(9)

    def setValue(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(EnemyWithOneParamModel, self)._initialize()
        self._addNumberProperty('value', 0)
