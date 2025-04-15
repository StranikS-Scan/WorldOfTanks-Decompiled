# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/daily_quests_mark_seen_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.daily.daily_quest_mark_seen_model import DailyQuestMarkSeenModel

class DailyQuestsMarkSeenModel(ViewModel):
    __slots__ = ('onQuestsSeen',)

    def __init__(self, properties=1, commands=1):
        super(DailyQuestsMarkSeenModel, self).__init__(properties=properties, commands=commands)

    def getUnseenQuests(self):
        return self._getArray(0)

    def setUnseenQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getUnseenQuestsType():
        return DailyQuestMarkSeenModel

    def _initialize(self):
        super(DailyQuestsMarkSeenModel, self)._initialize()
        self._addArrayProperty('unseenQuests', Array())
        self.onQuestsSeen = self._addCommand('onQuestsSeen')
