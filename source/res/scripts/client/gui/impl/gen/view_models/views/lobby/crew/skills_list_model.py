# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/skills_list_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.crew.components.component_base_model import ComponentBaseModel
from gui.impl.gen.view_models.views.lobby.crew.skill_model import SkillModel

class SkillsListModel(ComponentBaseModel):
    __slots__ = ('onSkillClick', 'onSkillHover', 'onSkillOut', 'onTrain', 'onCancel')

    def __init__(self, properties=4, commands=5):
        super(SkillsListModel, self).__init__(properties=properties, commands=commands)

    def getIrrelevantSkillsList(self):
        return self._getArray(1)

    def setIrrelevantSkillsList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getIrrelevantSkillsListType():
        return SkillModel

    def getCommonSkillsList(self):
        return self._getArray(2)

    def setCommonSkillsList(self, value):
        self._setArray(2, value)

    @staticmethod
    def getCommonSkillsListType():
        return SkillModel

    def getRegularSkillsList(self):
        return self._getArray(3)

    def setRegularSkillsList(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRegularSkillsListType():
        return SkillModel

    def _initialize(self):
        super(SkillsListModel, self)._initialize()
        self._addArrayProperty('irrelevantSkillsList', Array())
        self._addArrayProperty('commonSkillsList', Array())
        self._addArrayProperty('regularSkillsList', Array())
        self.onSkillClick = self._addCommand('onSkillClick')
        self.onSkillHover = self._addCommand('onSkillHover')
        self.onSkillOut = self._addCommand('onSkillOut')
        self.onTrain = self._addCommand('onTrain')
        self.onCancel = self._addCommand('onCancel')
