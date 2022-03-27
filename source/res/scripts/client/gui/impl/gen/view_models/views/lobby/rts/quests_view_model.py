# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/quests_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.rts_quest_model import RtsQuestModel

class State(IntEnum):
    QUESTS_AVAILABLE = 0
    QUESTS_FINISHED = 1
    ERROR = 2
    EVENT_ENDED = 3


class QuestsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(QuestsViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getNumber(0))

    def setState(self, value):
        self._setNumber(0, value.value)

    def getCountdown(self):
        return self._getNumber(1)

    def setCountdown(self, value):
        self._setNumber(1, value)

    def getQuests(self):
        return self._getArray(2)

    def setQuests(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(QuestsViewModel, self)._initialize()
        self._addNumberProperty('state')
        self._addNumberProperty('countdown', 0)
        self._addArrayProperty('quests', Array())
