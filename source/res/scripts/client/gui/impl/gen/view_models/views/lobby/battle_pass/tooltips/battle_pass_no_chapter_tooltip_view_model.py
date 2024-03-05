# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_pass_no_chapter_tooltip_view_model.py
from frameworks.wulf import ViewModel

class BattlePassNoChapterTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BattlePassNoChapterTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getPoints(self):
        return self._getNumber(0)

    def setPoints(self, value):
        self._setNumber(0, value)

    def getChapterName(self):
        return self._getString(1)

    def setChapterName(self, value):
        self._setString(1, value)

    def getIsResourceActive(self):
        return self._getBool(2)

    def setIsResourceActive(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(BattlePassNoChapterTooltipViewModel, self)._initialize()
        self._addNumberProperty('points', 0)
        self._addStringProperty('chapterName', '')
        self._addBoolProperty('isResourceActive', False)
