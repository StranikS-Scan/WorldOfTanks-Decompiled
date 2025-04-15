# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/daily_quests_premium_model.py
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_regular_model import DailyQuestsRegularModel

class DailyQuestsPremiumModel(DailyQuestsRegularModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(DailyQuestsPremiumModel, self).__init__(properties=properties, commands=commands)

    def getHasPremiumAccount(self):
        return self._getBool(7)

    def setHasPremiumAccount(self, value):
        self._setBool(7, value)

    def getPremMissionsTabDiscovered(self):
        return self._getBool(8)

    def setPremMissionsTabDiscovered(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(DailyQuestsPremiumModel, self)._initialize()
        self._addBoolProperty('hasPremiumAccount', False)
        self._addBoolProperty('premMissionsTabDiscovered', False)
