# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/learned_skills_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.skill_model import SkillModel

class LearnedSkillsModel(NavigationViewModel):
    __slots__ = ('goToMatrix',)

    def __init__(self, properties=4, commands=4):
        super(LearnedSkillsModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(2)

    def setTitle(self, value):
        self._setResource(2, value)

    def getSkillsList(self):
        return self._getArray(3)

    def setSkillsList(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(LearnedSkillsModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addArrayProperty('skillsList', Array())
        self.goToMatrix = self._addCommand('goToMatrix')
