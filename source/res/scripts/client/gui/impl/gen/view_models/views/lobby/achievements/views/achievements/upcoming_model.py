# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/achievements/upcoming_model.py
from gui.impl.gen.view_models.views.lobby.achievements.advanced_achievement_model import AdvancedAchievementModel

class UpcomingModel(AdvancedAchievementModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(UpcomingModel, self).__init__(properties=properties, commands=commands)

    def getSpecificItemName(self):
        return self._getString(14)

    def setSpecificItemName(self, value):
        self._setString(14, value)

    def getSpecificItemLevel(self):
        return self._getNumber(15)

    def setSpecificItemLevel(self, value):
        self._setNumber(15, value)

    def getIsResearchable(self):
        return self._getBool(16)

    def setIsResearchable(self, value):
        self._setBool(16, value)

    def _initialize(self):
        super(UpcomingModel, self)._initialize()
        self._addStringProperty('specificItemName', '')
        self._addNumberProperty('specificItemLevel', 0)
        self._addBoolProperty('isResearchable', False)
