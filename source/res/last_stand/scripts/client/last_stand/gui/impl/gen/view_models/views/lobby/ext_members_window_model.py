# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/ext_members_window_model.py
from enum import Enum
from last_stand.gui.impl.gen.view_models.views.lobby.event_difficulty_model import EventDifficultyModel
from gui.impl.gen.view_models.views.lobby.platoon.members_window_model import MembersWindowModel

class PrebattleTypes(Enum):
    LASTSTAND = 'lastStand'


class ExtMembersWindowModel(MembersWindowModel):
    __slots__ = ()

    def __init__(self, properties=23, commands=3):
        super(ExtMembersWindowModel, self).__init__(properties=properties, commands=commands)

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

    def getIsInSearch(self):
        return self._getBool(20)

    def setIsInSearch(self, value):
        self._setBool(20, value)

    def getIsCommander(self):
        return self._getBool(21)

    def setIsCommander(self, value):
        self._setBool(21, value)

    def getHasFreeSlots(self):
        return self._getBool(22)

    def setHasFreeSlots(self, value):
        self._setBool(22, value)

    def _initialize(self):
        super(ExtMembersWindowModel, self)._initialize()
        self._addViewModelProperty('eventDifficulty', EventDifficultyModel())
        self._addNumberProperty('selectedDifficulty', 1)
        self._addBoolProperty('selectionDisabled', False)
        self._addBoolProperty('isInSearch', False)
        self._addBoolProperty('isCommander', False)
        self._addBoolProperty('hasFreeSlots', False)
