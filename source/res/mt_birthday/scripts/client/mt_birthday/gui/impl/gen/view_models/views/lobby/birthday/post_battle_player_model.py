# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/post_battle_player_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class PostBattlePlayerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(PostBattlePlayerModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    @property
    def userInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getUserInfoType():
        return UserNameModel

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def getIsLoading(self):
        return self._getBool(3)

    def setIsLoading(self, value):
        self._setBool(3, value)

    def getIsBanned(self):
        return self._getBool(4)

    def setIsBanned(self, value):
        self._setBool(4, value)

    def getIsPlayerInBlacklist(self):
        return self._getBool(5)

    def setIsPlayerInBlacklist(self, value):
        self._setBool(5, value)

    def getIsBot(self):
        return self._getBool(6)

    def setIsBot(self, value):
        self._setBool(6, value)

    def getTotalDamage(self):
        return self._getNumber(7)

    def setTotalDamage(self, value):
        self._setNumber(7, value)

    def getKills(self):
        return self._getNumber(8)

    def setKills(self, value):
        self._setNumber(8, value)

    def getXp(self):
        return self._getNumber(9)

    def setXp(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(PostBattlePlayerModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addViewModelProperty('userInfo', UserNameModel())
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isLoading', False)
        self._addBoolProperty('isBanned', False)
        self._addBoolProperty('isPlayerInBlacklist', False)
        self._addBoolProperty('isBot', False)
        self._addNumberProperty('totalDamage', 0)
        self._addNumberProperty('kills', 0)
        self._addNumberProperty('xp', 0)
