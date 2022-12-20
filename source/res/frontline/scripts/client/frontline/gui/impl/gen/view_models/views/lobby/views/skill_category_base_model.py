# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/skill_category_base_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_base_model import SkillBaseModel

class SkillCategoryType(Enum):
    FIRESUPPORT = 'firesupport'
    RECONNAISSANCE = 'reconnaissance'
    TACTICS = 'tactics'


class SkillCategoryBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SkillCategoryBaseModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return SkillCategoryType(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getSkills(self):
        return self._getArray(1)

    def setSkills(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSkillsType():
        return SkillBaseModel

    def _initialize(self):
        super(SkillCategoryBaseModel, self)._initialize()
        self._addStringProperty('type')
        self._addArrayProperty('skills', Array())
