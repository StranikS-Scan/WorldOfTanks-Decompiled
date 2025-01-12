# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/personal_case/skills_matrix_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.crew.components.component_base_model import ComponentBaseModel
from gui.impl.gen.view_models.views.lobby.crew.personal_case.tankman_skills_group_model import TankmanSkillsGroupModel

class SkillsMatrixModel(ComponentBaseModel):
    __slots__ = ('onIncrease', 'onReset', 'onSkillClick', 'onSetAnimationInProgress')

    def __init__(self, properties=8, commands=4):
        super(SkillsMatrixModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainSkills(self):
        return self._getViewModel(1)

    @staticmethod
    def getMainSkillsType():
        return TankmanSkillsGroupModel

    def getIsResetDisable(self):
        return self._getBool(2)

    def setIsResetDisable(self, value):
        self._setBool(2, value)

    def getHasResetDiscount(self):
        return self._getBool(3)

    def setHasResetDiscount(self, value):
        self._setBool(3, value)

    def getIsResetFree(self):
        return self._getBool(4)

    def setIsResetFree(self, value):
        self._setBool(4, value)

    def getHasIncreaseDiscount(self):
        return self._getBool(5)

    def setHasIncreaseDiscount(self, value):
        self._setBool(5, value)

    def getResetGracePeriodLeft(self):
        return self._getNumber(6)

    def setResetGracePeriodLeft(self, value):
        self._setNumber(6, value)

    def getBonusSkills(self):
        return self._getArray(7)

    def setBonusSkills(self, value):
        self._setArray(7, value)

    @staticmethod
    def getBonusSkillsType():
        return TankmanSkillsGroupModel

    def _initialize(self):
        super(SkillsMatrixModel, self)._initialize()
        self._addViewModelProperty('mainSkills', TankmanSkillsGroupModel())
        self._addBoolProperty('isResetDisable', False)
        self._addBoolProperty('hasResetDiscount', False)
        self._addBoolProperty('isResetFree', False)
        self._addBoolProperty('hasIncreaseDiscount', False)
        self._addNumberProperty('resetGracePeriodLeft', 0)
        self._addArrayProperty('bonusSkills', Array())
        self.onIncrease = self._addCommand('onIncrease')
        self.onReset = self._addCommand('onReset')
        self.onSkillClick = self._addCommand('onSkillClick')
        self.onSetAnimationInProgress = self._addCommand('onSetAnimationInProgress')
