# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/skill_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.skill_stats_model import SkillStatsModel

class SkillModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(SkillModel, self).__init__(properties=properties, commands=commands)

    @property
    def skillsStats(self):
        return self._getViewModel(0)

    @staticmethod
    def getSkillsStatsType():
        return SkillStatsModel

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getIntCD(self):
        return self._getNumber(2)

    def setIntCD(self, value):
        self._setNumber(2, value)

    def getStartLevel(self):
        return self._getNumber(3)

    def setStartLevel(self, value):
        self._setNumber(3, value)

    def getIsEquipped(self):
        return self._getBool(4)

    def setIsEquipped(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(SkillModel, self)._initialize()
        self._addViewModelProperty('skillsStats', SkillStatsModel())
        self._addStringProperty('name', '')
        self._addNumberProperty('intCD', 0)
        self._addNumberProperty('startLevel', 0)
        self._addBoolProperty('isEquipped', False)
