# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_how_to_earn_points_view_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_model import GameModeModel

class BattlePassHowToEarnPointsViewModel(ViewModel):
    __slots__ = ('onGoToMissions', 'onWotPlusClick')

    def __init__(self, properties=3, commands=2):
        super(BattlePassHowToEarnPointsViewModel, self).__init__(properties=properties, commands=commands)

    def getChapterID(self):
        return self._getNumber(0)

    def setChapterID(self, value):
        self._setNumber(0, value)

    def getGameModes(self):
        return self._getArray(1)

    def setGameModes(self, value):
        self._setArray(1, value)

    @staticmethod
    def getGameModesType():
        return GameModeModel

    def getIsWotPlusShown(self):
        return self._getBool(2)

    def setIsWotPlusShown(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(BattlePassHowToEarnPointsViewModel, self)._initialize()
        self._addNumberProperty('chapterID', 0)
        self._addArrayProperty('gameModes', Array())
        self._addBoolProperty('isWotPlusShown', False)
        self.onGoToMissions = self._addCommand('onGoToMissions')
        self.onWotPlusClick = self._addCommand('onWotPlusClick')
