# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/player_details_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
from gui.impl.gen.view_models.views.lobby.postbattle.achievement_model import AchievementModel

class PlayerDetailsModel(ViewModel):
    __slots__ = ()
    INTEGER = 'integer'
    INT_ARRAY = 'int_array'
    LOCAL_TIME = 'local_time'
    BATTLE_DURATION = 'battle_duration'
    LIFETIME = 'lifetime'
    MILEAGE = 'mileage'
    ALIVE = -1
    SHOT = 0
    FIRE = 1
    RAM = 2
    WORLD_COLLISION = 3
    DEATH_ZONE = 4
    DROWNING = 5
    GAS_ATTACK = 6
    OVERTURN = 7
    MANUAL = 8
    ARTILLERY_PROTECTION = 9
    ARTILLERY_SECTOR = 10
    BOMBERS = 11
    RECOVERY = 12
    ARTILLERY_EQ = 13
    BOMBER_EQ = 14
    NONE = 15

    def __init__(self, properties=5, commands=0):
        super(PlayerDetailsModel, self).__init__(properties=properties, commands=commands)

    @property
    def killer(self):
        return self._getViewModel(0)

    @staticmethod
    def getKillerType():
        return UserNameModel

    def getAttackReason(self):
        return self._getNumber(1)

    def setAttackReason(self, value):
        self._setNumber(1, value)

    def getIsLeftBattle(self):
        return self._getBool(2)

    def setIsLeftBattle(self, value):
        self._setBool(2, value)

    def getAchievements(self):
        return self._getArray(3)

    def setAchievements(self, value):
        self._setArray(3, value)

    @staticmethod
    def getAchievementsType():
        return AchievementModel

    def getStatistics(self):
        return self._getArray(4)

    def setStatistics(self, value):
        self._setArray(4, value)

    def _initialize(self):
        super(PlayerDetailsModel, self)._initialize()
        self._addViewModelProperty('killer', UserNameModel())
        self._addNumberProperty('attackReason', 0)
        self._addBoolProperty('isLeftBattle', False)
        self._addArrayProperty('achievements', Array())
        self._addArrayProperty('statistics', Array())
