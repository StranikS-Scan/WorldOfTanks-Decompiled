# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/early_access_chapter_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ChapterState(Enum):
    DISABLED = 'disabled'
    ACTIVE = 'active'
    COMPLETED = 'completed'


class EarlyAccessChapterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(EarlyAccessChapterModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getState(self):
        return ChapterState(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getCompletedQuestsAll(self):
        return self._getNumber(2)

    def setCompletedQuestsAll(self, value):
        self._setNumber(2, value)

    def getCompletedQuestsNew(self):
        return self._getNumber(3)

    def setCompletedQuestsNew(self, value):
        self._setNumber(3, value)

    def getTotalQuests(self):
        return self._getNumber(4)

    def setTotalQuests(self, value):
        self._setNumber(4, value)

    def getShowTokens(self):
        return self._getBool(5)

    def setShowTokens(self, value):
        self._setBool(5, value)

    def getReceivedTokens(self):
        return self._getNumber(6)

    def setReceivedTokens(self, value):
        self._setNumber(6, value)

    def getTotalTokens(self):
        return self._getNumber(7)

    def setTotalTokens(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(EarlyAccessChapterModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('state')
        self._addNumberProperty('completedQuestsAll', 0)
        self._addNumberProperty('completedQuestsNew', 0)
        self._addNumberProperty('totalQuests', 0)
        self._addBoolProperty('showTokens', False)
        self._addNumberProperty('receivedTokens', 0)
        self._addNumberProperty('totalTokens', 0)
