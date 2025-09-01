# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/widget/battle_pass_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.user_missions.widget.base_battle_pass_model import BaseBattlePassModel

class WidgetState(Enum):
    INTRO = 'intro'
    PROGRESSION = 'progression'
    COMPLETED = 'completed'


class AppearAnimationState(Enum):
    WAITING = 'waiting'
    READY = 'ready'
    PLAYED = 'played'


class BattlePassModel(BaseBattlePassModel):
    __slots__ = ('onOpenBattlePass', 'onIntroAnimationPlayed')

    def __init__(self, properties=16, commands=2):
        super(BattlePassModel, self).__init__(properties=properties, commands=commands)

    @property
    def lastSeenState(self):
        return self._getViewModel(3)

    @staticmethod
    def getLastSeenStateType():
        return BaseBattlePassModel

    def getWidgetState(self):
        return WidgetState(self._getString(4))

    def setWidgetState(self, value):
        self._setString(4, value.value)

    def getLevelPoints(self):
        return self._getNumber(5)

    def setLevelPoints(self, value):
        self._setNumber(5, value)

    def getTooltipID(self):
        return self._getNumber(6)

    def setTooltipID(self, value):
        self._setNumber(6, value)

    def getChapterID(self):
        return self._getNumber(7)

    def setChapterID(self, value):
        self._setNumber(7, value)

    def getSeason(self):
        return self._getNumber(8)

    def setSeason(self, value):
        self._setNumber(8, value)

    def getIsBought(self):
        return self._getBool(9)

    def setIsBought(self, value):
        self._setBool(9, value)

    def getIsExtraChapter(self):
        return self._getBool(10)

    def setIsExtraChapter(self, value):
        self._setBool(10, value)

    def getIsPaused(self):
        return self._getBool(11)

    def setIsPaused(self, value):
        self._setBool(11, value)

    def getHasExtraChapter(self):
        return self._getBool(12)

    def setHasExtraChapter(self, value):
        self._setBool(12, value)

    def getIsExtraChapterHighlighted(self):
        return self._getBool(13)

    def setIsExtraChapterHighlighted(self, value):
        self._setBool(13, value)

    def getAppearAnimationState(self):
        return AppearAnimationState(self._getString(14))

    def setAppearAnimationState(self, value):
        self._setString(14, value.value)

    def getTimeLeft(self):
        return self._getNumber(15)

    def setTimeLeft(self, value):
        self._setNumber(15, value)

    def _initialize(self):
        super(BattlePassModel, self)._initialize()
        self._addViewModelProperty('lastSeenState', BaseBattlePassModel())
        self._addStringProperty('widgetState')
        self._addNumberProperty('levelPoints', 0)
        self._addNumberProperty('tooltipID', 0)
        self._addNumberProperty('chapterID', -1)
        self._addNumberProperty('season', 0)
        self._addBoolProperty('isBought', False)
        self._addBoolProperty('isExtraChapter', False)
        self._addBoolProperty('isPaused', False)
        self._addBoolProperty('hasExtraChapter', False)
        self._addBoolProperty('isExtraChapterHighlighted', False)
        self._addStringProperty('appearAnimationState')
        self._addNumberProperty('timeLeft', 0)
        self.onOpenBattlePass = self._addCommand('onOpenBattlePass')
        self.onIntroAnimationPlayed = self._addCommand('onIntroAnimationPlayed')
