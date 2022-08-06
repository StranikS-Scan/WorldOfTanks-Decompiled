# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_how_to_earn_points_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.game_mode_model import GameModeModel

class BattlePassHowToEarnPointsViewModel(ViewModel):
    __slots__ = ('onLinkClick',)

    def __init__(self, properties=3, commands=1):
        super(BattlePassHowToEarnPointsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def gameModes(self):
        return self._getViewModel(0)

    @staticmethod
    def getGameModesType():
        return GameModeModel

    def getSyncInitiator(self):
        return self._getNumber(1)

    def setSyncInitiator(self, value):
        self._setNumber(1, value)

    def getChapterID(self):
        return self._getNumber(2)

    def setChapterID(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BattlePassHowToEarnPointsViewModel, self)._initialize()
        self._addViewModelProperty('gameModes', UserListModel())
        self._addNumberProperty('syncInitiator', 0)
        self._addNumberProperty('chapterID', 0)
        self.onLinkClick = self._addCommand('onLinkClick')
