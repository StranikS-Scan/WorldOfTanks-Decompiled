# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/crew_perks_tooltip_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
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


class CrewPerksTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(CrewPerksTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getSkillType(self):
        return self._getString(2)

    def setSkillType(self, value):
        self._setString(2, value)

    def getLevel(self):
        return self._getReal(3)

    def setLevel(self, value):
        self._setReal(3, value)

    def getIsCommonExtraAvailable(self):
        return self._getBool(4)

    def setIsCommonExtraAvailable(self, value):
        self._setBool(4, value)

    def getIsAdvancedTooltipEnable(self):
        return self._getBool(5)

    def setIsAdvancedTooltipEnable(self, value):
        self._setBool(5, value)

    def getIsZeroPerk(self):
        return self._getBool(6)

    def setIsZeroPerk(self, value):
        self._setBool(6, value)

    def getIsIrrelevant(self):
        return self._getBool(7)

    def setIsIrrelevant(self, value):
        self._setBool(7, value)

    def getDescription(self):
        return self._getString(8)

    def setDescription(self, value):
        self._setString(8, value)

    def getDescriptionKwargs(self):
        return self._getString(9)

    def setDescriptionKwargs(self, value):
        self._setString(9, value)

    def getBoosters(self):
        return self._getArray(10)

    def setBoosters(self, value):
        self._setArray(10, value)

    @staticmethod
    def getBoostersType():
        return CrewPerksTooltipBoosterModel

    def getEfficiency(self):
        return self._getReal(11)

    def setEfficiency(self, value):
        self._setReal(11, value)

    def getBoosterType(self):
        return BoosterType(self._getString(12))

    def setBoosterType(self, value):
        self._setString(12, value.value)

    def _initialize(self):
        super(CrewPerksTooltipModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('skillType', '')
        self._addRealProperty('level', 0.0)
        self._addBoolProperty('isCommonExtraAvailable', False)
        self._addBoolProperty('isAdvancedTooltipEnable', False)
        self._addBoolProperty('isZeroPerk', False)
        self._addBoolProperty('isIrrelevant', False)
        self._addStringProperty('description', '')
        self._addStringProperty('descriptionKwargs', '')
        self._addArrayProperty('boosters', Array())
        self._addRealProperty('efficiency', 0.0)
        self._addStringProperty('boosterType', BoosterType.NONE.value)
