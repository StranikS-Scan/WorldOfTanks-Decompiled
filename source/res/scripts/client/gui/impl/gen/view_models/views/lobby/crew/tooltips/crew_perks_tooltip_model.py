# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/crew_perks_tooltip_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_extended_model import SkillExtendedModel
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_tooltip_booster_model import CrewPerksTooltipBoosterModel

class PerkType(Enum):
    MAIN = 'main'
    SITUATIONAL = 'situational'
    COMMON = 'common'
    COMMANDERSPECIAL = 'commanderSpecial'


class BoosterType(Enum):
    NONE = 'none'
    ORDINARY = 'ordinary'
    EXTRA = 'extra'


class CrewPerksTooltipModel(SkillExtendedModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(CrewPerksTooltipModel, self).__init__(properties=properties, commands=commands)

    def getSkillType(self):
        return self._getString(9)

    def setSkillType(self, value):
        self._setString(9, value)

    def getRealLevel(self):
        return self._getReal(10)

    def setRealLevel(self, value):
        self._setReal(10, value)

    def getIsAdvancedTooltipEnable(self):
        return self._getBool(11)

    def setIsAdvancedTooltipEnable(self, value):
        self._setBool(11, value)

    def getIsGroupSkill(self):
        return self._getBool(12)

    def setIsGroupSkill(self, value):
        self._setBool(12, value)

    def getIsAnyMemberWithLowEfficiency(self):
        return self._getBool(13)

    def setIsAnyMemberWithLowEfficiency(self, value):
        self._setBool(13, value)

    def getIsAnyMemberUntrained(self):
        return self._getBool(14)

    def setIsAnyMemberUntrained(self, value):
        self._setBool(14, value)

    def getBoosters(self):
        return self._getArray(15)

    def setBoosters(self, value):
        self._setArray(15, value)

    @staticmethod
    def getBoostersType():
        return CrewPerksTooltipBoosterModel

    def getEfficiency(self):
        return self._getReal(16)

    def setEfficiency(self, value):
        self._setReal(16, value)

    def getBoosterType(self):
        return BoosterType(self._getString(17))

    def setBoosterType(self, value):
        self._setString(17, value.value)

    def _initialize(self):
        super(CrewPerksTooltipModel, self)._initialize()
        self._addStringProperty('skillType', '')
        self._addRealProperty('realLevel', 0.0)
        self._addBoolProperty('isAdvancedTooltipEnable', False)
        self._addBoolProperty('isGroupSkill', False)
        self._addBoolProperty('isAnyMemberWithLowEfficiency', False)
        self._addBoolProperty('isAnyMemberUntrained', False)
        self._addArrayProperty('boosters', Array())
        self._addRealProperty('efficiency', 0.0)
        self._addStringProperty('boosterType', BoosterType.NONE.value)
