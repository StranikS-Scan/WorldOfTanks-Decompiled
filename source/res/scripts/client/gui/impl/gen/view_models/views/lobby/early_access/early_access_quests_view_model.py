# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/early_access_quests_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.early_access.early_access_chapter_model import EarlyAccessChapterModel
from gui.impl.gen.view_models.views.lobby.early_access.early_access_quest_model import EarlyAccessQuestModel

class QuestsViewTooltipStates(Enum):
    QUEST = 'quest'
    CHAPTER = 'chapter'


class EarlyAccessQuestsViewModel(ViewModel):
    __slots__ = ('onClose', 'goToVehicle', 'goToInfo')

    def __init__(self, properties=5, commands=3):
        super(EarlyAccessQuestsViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getChapters(self):
        return self._getArray(1)

    def setChapters(self, value):
        self._setArray(1, value)

    @staticmethod
    def getChaptersType():
        return EarlyAccessChapterModel

    def getQuests(self):
        return self._getArray(2)

    def setQuests(self, value):
        self._setArray(2, value)

    @staticmethod
    def getQuestsType():
        return EarlyAccessQuestModel

    def getFromTimestamp(self):
        return self._getNumber(3)

    def setFromTimestamp(self, value):
        self._setNumber(3, value)

    def getToTimestamp(self):
        return self._getNumber(4)

    def setToTimestamp(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(EarlyAccessQuestsViewModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addArrayProperty('chapters', Array())
        self._addArrayProperty('quests', Array())
        self._addNumberProperty('fromTimestamp', 0)
        self._addNumberProperty('toTimestamp', 0)
        self.onClose = self._addCommand('onClose')
        self.goToVehicle = self._addCommand('goToVehicle')
        self.goToInfo = self._addCommand('goToInfo')
