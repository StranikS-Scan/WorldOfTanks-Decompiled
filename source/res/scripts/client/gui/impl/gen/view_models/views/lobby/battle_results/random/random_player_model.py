# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/random/random_player_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.account_model import AccountModel
from gui.impl.gen.view_models.views.lobby.battle_results.player_model import PlayerModel
from gui.impl.gen.view_models.views.lobby.battle_results.postbattle_achievement_model import PostbattleAchievementModel
from gui.impl.gen.view_models.views.lobby.battle_results.random.random_user_status_model import RandomUserStatusModel

class RandomPlayerModel(PlayerModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(RandomPlayerModel, self).__init__(properties=properties, commands=commands)

    @property
    def userNames(self):
        return self._getViewModel(9)

    @staticmethod
    def getUserNamesType():
        return AccountModel

    @property
    def userStatus(self):
        return self._getViewModel(10)

    @staticmethod
    def getUserStatusType():
        return RandomUserStatusModel

    def getPrebattleID(self):
        return self._getNumber(11)

    def setPrebattleID(self, value):
        self._setNumber(11, value)

    def getAchievements(self):
        return self._getArray(12)

    def setAchievements(self, value):
        self._setArray(12, value)

    @staticmethod
    def getAchievementsType():
        return PostbattleAchievementModel

    def _initialize(self):
        super(RandomPlayerModel, self)._initialize()
        self._addViewModelProperty('userNames', AccountModel())
        self._addViewModelProperty('userStatus', RandomUserStatusModel())
        self._addNumberProperty('prebattleID', 0)
        self._addArrayProperty('achievements', Array())
