# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions/personal_missions_main_quests_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_quest_view_model import Pm3QuestViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_quests_view_model import Pm3QuestsViewModel

class PageViewIdEnum(IntEnum):
    QUESTS = 0
    QUEST = 1


class PersonalMissionsMainQuestsViewModel(ViewModel):
    __slots__ = ('onClose', 'openQuest', 'onBackToOperations')

    def __init__(self, properties=3, commands=3):
        super(PersonalMissionsMainQuestsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def quest(self):
        return self._getViewModel(0)

    @staticmethod
    def getQuestType():
        return Pm3QuestViewModel

    @property
    def quests(self):
        return self._getViewModel(1)

    @staticmethod
    def getQuestsType():
        return Pm3QuestsViewModel

    def getPageViewId(self):
        return PageViewIdEnum(self._getNumber(2))

    def setPageViewId(self, value):
        self._setNumber(2, value.value)

    def _initialize(self):
        super(PersonalMissionsMainQuestsViewModel, self)._initialize()
        self._addViewModelProperty('quest', Pm3QuestViewModel())
        self._addViewModelProperty('quests', Pm3QuestsViewModel())
        self._addNumberProperty('pageViewId')
        self.onClose = self._addCommand('onClose')
        self.openQuest = self._addCommand('openQuest')
        self.onBackToOperations = self._addCommand('onBackToOperations')
