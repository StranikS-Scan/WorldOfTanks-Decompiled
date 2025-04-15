# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/daily_quest_mark_seen_model.py
from frameworks.wulf import ViewModel

class DailyQuestMarkSeenModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(DailyQuestMarkSeenModel, self).__init__(properties=properties, commands=commands)

    def getQuestID(self):
        return self._getString(0)

    def setQuestID(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(DailyQuestMarkSeenModel, self)._initialize()
        self._addStringProperty('questID', '')
