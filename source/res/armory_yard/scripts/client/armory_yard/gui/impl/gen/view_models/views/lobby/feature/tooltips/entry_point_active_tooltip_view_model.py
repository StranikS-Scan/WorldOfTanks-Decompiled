# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/tooltips/entry_point_active_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.tooltips.armory_yard_tooltip_chapter_model import ArmoryYardTooltipChapterModel

class EntryPointActiveTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(EntryPointActiveTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getQuestsInProgress(self):
        return self._getNumber(0)

    def setQuestsInProgress(self, value):
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
        return ArmoryYardTooltipChapterModel

    def getReceivedTokens(self):
        return self._getNumber(3)

    def setReceivedTokens(self, value):
        self._setNumber(3, value)

    def getTotalTokens(self):
        return self._getNumber(4)

    def setTotalTokens(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(EntryPointActiveTooltipViewModel, self)._initialize()
        self._addNumberProperty('questsInProgress', 0)
        self._addNumberProperty('endTimestamp', 0)
        self._addArrayProperty('chapters', Array())
        self._addNumberProperty('receivedTokens', 0)
        self._addNumberProperty('totalTokens', 0)
