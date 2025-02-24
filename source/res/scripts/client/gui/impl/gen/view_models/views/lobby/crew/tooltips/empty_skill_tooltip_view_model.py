# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/empty_skill_tooltip_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_progression_model import SkillProgressionModel

class EmptySkillTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(EmptySkillTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def skillProgression(self):
        return self._getViewModel(0)

    @staticmethod
    def getSkillProgressionType():
        return SkillProgressionModel

    def getIsZeroSkill(self):
        return self._getBool(1)

    def setIsZeroSkill(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(EmptySkillTooltipViewModel, self)._initialize()
        self._addViewModelProperty('skillProgression', SkillProgressionModel())
        self._addBoolProperty('isZeroSkill', False)
