# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_quest_model.py
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel

class WtQuestModel(DailyQuestModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(WtQuestModel, self).__init__(properties=properties, commands=commands)

    def getCompletedMissions(self):
        return self._getNumber(12)

    def setCompletedMissions(self, value):
        self._setNumber(12, value)

    def getMaxMissions(self):
        return self._getNumber(13)

    def setMaxMissions(self, value):
        self._setNumber(13, value)

    def _initialize(self):
        super(WtQuestModel, self)._initialize()
        self._addNumberProperty('completedMissions', 0)
        self._addNumberProperty('maxMissions', 0)
