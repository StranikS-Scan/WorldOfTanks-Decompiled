# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/crew_perks_additional_tooltip_model.py
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_extended_model import SkillExtendedModel
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_progression_model import SkillProgressionModel

class CrewPerksAdditionalTooltipModel(SkillExtendedModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(CrewPerksAdditionalTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def skillProgression(self):
        return self._getViewModel(9)

    @staticmethod
    def getSkillProgressionType():
        return SkillProgressionModel

    def getInfo(self):
        return self._getString(10)

    def setInfo(self, value):
        self._setString(10, value)

    def getSkillType(self):
        return self._getString(11)

    def setSkillType(self, value):
        self._setString(11, value)

    def getAnimationName(self):
        return self._getString(12)

    def setAnimationName(self, value):
        self._setString(12, value)

    def getIsDisabled(self):
        return self._getBool(13)

    def setIsDisabled(self, value):
        self._setBool(13, value)

    def getShowSkillProgression(self):
        return self._getBool(14)

    def setShowSkillProgression(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(CrewPerksAdditionalTooltipModel, self)._initialize()
        self._addViewModelProperty('skillProgression', SkillProgressionModel())
        self._addStringProperty('info', '')
        self._addStringProperty('skillType', '')
        self._addStringProperty('animationName', '')
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('showSkillProgression', False)
