# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/hw_members_window_model.py
from enum import Enum
from halloween.gui.impl.gen.view_models.views.lobby.event_difficulty_model import EventDifficultyModel
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import MembersWindowModel

class PrebattleTypes(Enum):
    HALLOWEEN = 'halloween'


class HwMembersWindowModel(MembersWindowModel):
    __slots__ = ()

    def __init__(self, properties=20, commands=3):
        super(HwMembersWindowModel, self).__init__(properties=properties, commands=commands)

    @property
    def eventDifficulty(self):
        return self._getViewModel(17)

    @staticmethod
    def getEventDifficultyType():
        return EventDifficultyModel

    def getSelectedDifficulty(self):
        return self._getNumber(18)

    def setSelectedDifficulty(self, value):
        self._setNumber(18, value)

    def getSelectionDisabled(self):
        return self._getBool(19)

    def setSelectionDisabled(self, value):
        self._setBool(19, value)

    def _initialize(self):
        super(HwMembersWindowModel, self)._initialize()
        self._addViewModelProperty('eventDifficulty', EventDifficultyModel())
        self._addNumberProperty('selectedDifficulty', 1)
        self._addBoolProperty('selectionDisabled', False)
