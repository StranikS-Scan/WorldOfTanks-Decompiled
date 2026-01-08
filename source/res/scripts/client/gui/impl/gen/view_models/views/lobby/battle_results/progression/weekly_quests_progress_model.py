# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/weekly_quests_progress_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.progression.weekly_quest_progress_model import WeeklyQuestProgressModel

class WeeklyQuestsProgressModel(ViewModel):
    __slots__ = ('onNavigate',)
    PATH = 'coui://gui/gameface/_dist/production/mono/plugins/post_battle/weekly_quests/weekly_quests.js'

    def __init__(self, properties=1, commands=1):
        super(WeeklyQuestsProgressModel, self).__init__(properties=properties, commands=commands)

    def getWeeklyQuests(self):
        return self._getArray(0)

    def setWeeklyQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getWeeklyQuestsType():
        return WeeklyQuestProgressModel

    def _initialize(self):
        super(WeeklyQuestsProgressModel, self)._initialize()
        self._addArrayProperty('weeklyQuests', Array())
        self.onNavigate = self._addCommand('onNavigate')
