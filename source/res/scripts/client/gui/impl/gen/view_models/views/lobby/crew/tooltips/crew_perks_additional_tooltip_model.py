# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/crew_perks_additional_tooltip_model.py
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_extended_model import SkillExtendedModel

class CrewPerksAdditionalTooltipModel(SkillExtendedModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(CrewPerksAdditionalTooltipModel, self).__init__(properties=properties, commands=commands)

    def getInfo(self):
        return self._getString(8)

    def setInfo(self, value):
        self._setString(8, value)

    def getSkillType(self):
        return self._getString(9)

    def setSkillType(self, value):
        self._setString(9, value)

    def getAnimationName(self):
        return self._getString(10)

    def setAnimationName(self, value):
        self._setString(10, value)

    def getIsDisabled(self):
        return self._getBool(11)

    def setIsDisabled(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(CrewPerksAdditionalTooltipModel, self)._initialize()
        self._addStringProperty('info', '')
        self._addStringProperty('skillType', '')
        self._addStringProperty('animationName', '')
        self._addBoolProperty('isDisabled', False)
