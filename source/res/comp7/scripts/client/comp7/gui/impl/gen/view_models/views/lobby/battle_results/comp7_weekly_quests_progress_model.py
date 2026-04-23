# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/battle_results/comp7_weekly_quests_progress_model.py
from frameworks.wulf import Array, ViewModel
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_weekly_quest_progress_model import Comp7WeeklyQuestProgressModel

class Comp7WeeklyQuestsProgressModel(ViewModel):
    __slots__ = ()
    PATH = 'coui://comp7/gui/gameface/_dist/production/mono/plugins/lobby/weekly_quests/weekly_quests.js'

    def __init__(self, properties=1, commands=0):
        super(Comp7WeeklyQuestsProgressModel, self).__init__(properties=properties, commands=commands)

    def getWeeklyQuests(self):
        return self._getArray(0)

    def setWeeklyQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getWeeklyQuestsType():
        return Comp7WeeklyQuestProgressModel

    def _initialize(self):
        super(Comp7WeeklyQuestsProgressModel, self)._initialize()
        self._addArrayProperty('weeklyQuests', Array())
