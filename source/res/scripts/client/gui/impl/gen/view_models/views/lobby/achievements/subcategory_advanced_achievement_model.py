# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/subcategory_advanced_achievement_model.py
from gui.impl.gen.view_models.views.lobby.achievements.advanced_achievement_model import AdvancedAchievementModel

class SubcategoryAdvancedAchievementModel(AdvancedAchievementModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(SubcategoryAdvancedAchievementModel, self).__init__(properties=properties, commands=commands)

    def getPrevValue(self):
        return self._getNumber(14)

    def setPrevValue(self, value):
        self._setNumber(14, value)

    def getPrevAchievementScore(self):
        return self._getNumber(15)

    def setPrevAchievementScore(self, value):
        self._setNumber(15, value)

    def getBubbles(self):
        return self._getNumber(16)

    def setBubbles(self, value):
        self._setNumber(16, value)

    def _initialize(self):
        super(SubcategoryAdvancedAchievementModel, self)._initialize()
        self._addNumberProperty('prevValue', 0)
        self._addNumberProperty('prevAchievementScore', 0)
        self._addNumberProperty('bubbles', 0)
