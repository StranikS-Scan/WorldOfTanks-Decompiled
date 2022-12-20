# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/skills_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_category_model import SkillCategoryModel

class SkillsViewModel(ViewModel):
    __slots__ = ('onSkillSelect', 'onSkillActivate')

    def __init__(self, properties=5, commands=2):
        super(SkillsViewModel, self).__init__(properties=properties, commands=commands)

    def getFrontlineState(self):
        return self._getString(0)

    def setFrontlineState(self, value):
        self._setString(0, value)

    def getPointsAmount(self):
        return self._getNumber(1)

    def setPointsAmount(self, value):
        self._setNumber(1, value)

    def getSelectedSkillId(self):
        return self._getNumber(2)

    def setSelectedSkillId(self, value):
        self._setNumber(2, value)

    def getCanActivateSkills(self):
        return self._getBool(3)

    def setCanActivateSkills(self, value):
        self._setBool(3, value)

    def getCategories(self):
        return self._getArray(4)

    def setCategories(self, value):
        self._setArray(4, value)

    @staticmethod
    def getCategoriesType():
        return SkillCategoryModel

    def _initialize(self):
        super(SkillsViewModel, self)._initialize()
        self._addStringProperty('frontlineState', '')
        self._addNumberProperty('pointsAmount', 0)
        self._addNumberProperty('selectedSkillId', 0)
        self._addBoolProperty('canActivateSkills', True)
        self._addArrayProperty('categories', Array())
        self.onSkillSelect = self._addCommand('onSkillSelect')
        self.onSkillActivate = self._addCommand('onSkillActivate')
