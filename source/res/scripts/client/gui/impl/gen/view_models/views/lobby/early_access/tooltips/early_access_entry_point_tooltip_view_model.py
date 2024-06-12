# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/tooltips/early_access_entry_point_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.early_access.tooltips.early_access_tooltip_chapter_model import EarlyAccessTooltipChapterModel

class EarlyAccessEntryPointTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(EarlyAccessEntryPointTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentTimestamp(self):
        return self._getNumber(0)

    def setCurrentTimestamp(self, value):
        self._setNumber(0, value)

    def getEndTimestamp(self):
        return self._getNumber(1)

    def setEndTimestamp(self, value):
        self._setNumber(1, value)

    def getChapters(self):
        return self._getArray(2)

    def setChapters(self, value):
        self._setArray(2, value)

    @staticmethod
    def getChaptersType():
        return EarlyAccessTooltipChapterModel

    def getReceivedTokens(self):
        return self._getNumber(3)

    def setReceivedTokens(self, value):
        self._setNumber(3, value)

    def getTotalTokens(self):
        return self._getNumber(4)

    def setTotalTokens(self, value):
        self._setNumber(4, value)

    def getIsPostprogression(self):
        return self._getBool(5)

    def setIsPostprogression(self, value):
        self._setBool(5, value)

    def getIsPaused(self):
        return self._getBool(6)

    def setIsPaused(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(EarlyAccessEntryPointTooltipViewModel, self)._initialize()
        self._addNumberProperty('currentTimestamp', 0)
        self._addNumberProperty('endTimestamp', 0)
        self._addArrayProperty('chapters', Array())
        self._addNumberProperty('receivedTokens', 0)
        self._addNumberProperty('totalTokens', 0)
        self._addBoolProperty('isPostprogression', False)
        self._addBoolProperty('isPaused', False)
