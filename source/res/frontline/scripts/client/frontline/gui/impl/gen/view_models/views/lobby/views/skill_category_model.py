# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/skill_category_model.py
from frameworks.wulf import Array
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_category_base_model import SkillCategoryBaseModel
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_model import SkillModel

class SkillCategoryModel(SkillCategoryBaseModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(SkillCategoryModel, self).__init__(properties=properties, commands=commands)

    def getSkills(self):
        return self._getArray(2)

    def setSkills(self, value):
        self._setArray(2, value)

    @staticmethod
    def getSkillsType():
        return SkillModel

    def _initialize(self):
        super(SkillCategoryModel, self)._initialize()
        self._addArrayProperty('skills', Array())
