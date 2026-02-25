# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_how_to_earn_points_view_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_model import GameModeModel

class BattlePassHowToEarnPointsViewModel(ViewModel):
    __slots__ = ('onLinkClick', 'onWotPlusClick')

    def __init__(self, properties=4, commands=2):
        super(BattlePassHowToEarnPointsViewModel, self).__init__(properties=properties, commands=commands)

    def getSyncInitiator(self):
        return self._getNumber(0)

    def setSyncInitiator(self, value):
        self._setNumber(0, value)

    def getChapterID(self):
        return self._getNumber(1)

    def setChapterID(self, value):
        self._setNumber(1, value)

    def getGameModes(self):
        return self._getArray(2)

    def setGameModes(self, value):
        self._setArray(2, value)

    @staticmethod
    def getGameModesType():
        return GameModeModel

    def getIsWotPlusShown(self):
        return self._getBool(3)

    def setIsWotPlusShown(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(BattlePassHowToEarnPointsViewModel, self)._initialize()
        self._addNumberProperty('syncInitiator', 0)
        self._addNumberProperty('chapterID', 0)
        self._addArrayProperty('gameModes', Array())
        self._addBoolProperty('isWotPlusShown', False)
        self.onLinkClick = self._addCommand('onLinkClick')
        self.onWotPlusClick = self._addCommand('onWotPlusClick')
