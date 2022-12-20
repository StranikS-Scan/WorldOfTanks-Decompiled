# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/skill_level_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_param_model import SkillParamModel

class SkillLevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SkillLevelModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getParams(self):
        return self._getArray(1)

    def setParams(self, value):
        self._setArray(1, value)

    @staticmethod
    def getParamsType():
        return SkillParamModel

    def _initialize(self):
        super(SkillLevelModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addArrayProperty('params', Array())
