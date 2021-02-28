# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_pass_3d_style_not_chosen_tooltip_model.py
from frameworks.wulf import ViewModel

class BattlePass3DStyleNotChosenTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BattlePass3DStyleNotChosenTooltipModel, self).__init__(properties=properties, commands=commands)

    def getChapter(self):
        return self._getNumber(0)

    def setChapter(self, value):
        self._setNumber(0, value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getIsChapterCompleted(self):
        return self._getBool(2)

    def setIsChapterCompleted(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(BattlePass3DStyleNotChosenTooltipModel, self)._initialize()
        self._addNumberProperty('chapter', 0)
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isChapterCompleted', False)
