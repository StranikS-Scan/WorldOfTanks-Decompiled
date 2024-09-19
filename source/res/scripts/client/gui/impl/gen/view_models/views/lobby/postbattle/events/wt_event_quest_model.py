# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/events/wt_event_quest_model.py
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel

class WtEventQuestModel(DailyQuestModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(WtEventQuestModel, self).__init__(properties=properties, commands=commands)

    def getStatusLabel(self):
        return self._getString(12)

    def setStatusLabel(self, value):
        self._setString(12, value)

    def getCompletedMissions(self):
        return self._getNumber(13)

    def setCompletedMissions(self, value):
        self._setNumber(13, value)

    def getMaxMissions(self):
        return self._getNumber(14)

    def setMaxMissions(self, value):
        self._setNumber(14, value)

    def _initialize(self):
        super(WtEventQuestModel, self)._initialize()
        self._addStringProperty('statusLabel', '')
        self._addNumberProperty('completedMissions', 0)
        self._addNumberProperty('maxMissions', 0)
