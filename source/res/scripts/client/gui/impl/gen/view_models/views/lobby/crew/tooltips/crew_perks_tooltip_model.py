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


class CrewPerksTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
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

    def getDescription(self):
        return self._getString(6)

    def setDescription(self, value):
        self._setString(6, value)

    def getBoosters(self):
        return self._getArray(7)

    def setBoosters(self, value):
        self._setArray(7, value)

    @staticmethod
    def getBoostersType():
        return CrewPerksTooltipBoosterModel

    def _initialize(self):
        super(CrewPerksTooltipModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('skillType', '')
        self._addRealProperty('level', 0.0)
        self._addBoolProperty('isCommonExtraAvailable', False)
        self._addBoolProperty('isAdvancedTooltipEnable', False)
        self._addStringProperty('description', '')
        self._addArrayProperty('boosters', Array())
