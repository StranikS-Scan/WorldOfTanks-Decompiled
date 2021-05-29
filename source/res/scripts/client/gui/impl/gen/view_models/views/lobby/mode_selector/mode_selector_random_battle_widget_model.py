# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_random_battle_widget_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_base_widget_model import ModeSelectorBaseWidgetModel

class ProgressionState(Enum):
    FREE_BASE = 'free_base'
    BOUGHT_BASE = 'bought_base'
    PAUSED = 'paused'
    AWAIT_SEASON = 'await_season'
    CHOOSE_3D_STYLE = 'choose_3d_style'
    COMPLETED = 'completed'


class ModeSelectorRandomBattleWidgetModel(ModeSelectorBaseWidgetModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(ModeSelectorRandomBattleWidgetModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getProgress(self):
        return self._getNumber(2)

    def setProgress(self, value):
        self._setNumber(2, value)

    def getPoints(self):
        return self._getNumber(3)

    def setPoints(self, value):
        self._setNumber(3, value)

    def getHasBattlePass(self):
        return self._getBool(4)

    def setHasBattlePass(self, value):
        self._setBool(4, value)

    def getProgressionState(self):
        return ProgressionState(self._getString(5))

    def setProgressionState(self, value):
        self._setString(5, value.value)

    def getChapter(self):
        return self._getNumber(6)

    def setChapter(self, value):
        self._setNumber(6, value)

    def getTooltipID(self):
        return self._getNumber(7)

    def setTooltipID(self, value):
        self._setNumber(7, value)

    def getNotChosenRewardCount(self):
        return self._getNumber(8)

    def setNotChosenRewardCount(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(ModeSelectorRandomBattleWidgetModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('points', 0)
        self._addBoolProperty('hasBattlePass', False)
        self._addStringProperty('progressionState')
        self._addNumberProperty('chapter', 0)
        self._addNumberProperty('tooltipID', 0)
        self._addNumberProperty('notChosenRewardCount', 0)
