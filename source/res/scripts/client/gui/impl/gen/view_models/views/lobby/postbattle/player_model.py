# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/player_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
from gui.impl.gen.view_models.views.lobby.postbattle.player_details_model import PlayerDetailsModel

class PlayerModel(ViewModel):
    __slots__ = ()
    PLAYER_DAMAGE_DEALT = 'damageDealt'
    PLAYER_KILLS = 'kills'
    PLAYER_EARNED_XP = 'earnedXp'
    PLAYER_IDX = 'idx'
    PLAYER_SQUAD_IDX = 'squadIdx'

    def __init__(self, properties=16, commands=0):
        super(PlayerModel, self).__init__(properties=properties, commands=commands)

    @property
    def details(self):
        return self._getViewModel(0)

    @property
    def user(self):
        return self._getViewModel(1)

    def getEarnedXp(self):
        return self._getNumber(2)

    def setEarnedXp(self, value):
        self._setNumber(2, value)

    def getVehicleName(self):
        return self._getString(3)

    def setVehicleName(self, value):
        self._setString(3, value)

    def getLocalizedVehicleName(self):
        return self._getString(4)

    def setLocalizedVehicleName(self, value):
        self._setString(4, value)

    def getKills(self):
        return self._getNumber(5)

    def setKills(self, value):
        self._setNumber(5, value)

    def getDamageDealt(self):
        return self._getNumber(6)

    def setDamageDealt(self, value):
        self._setNumber(6, value)

    def getVehicleType(self):
        return self._getString(7)

    def setVehicleType(self, value):
        self._setString(7, value)

    def getVehicleLevel(self):
        return self._getNumber(8)

    def setVehicleLevel(self, value):
        self._setNumber(8, value)

    def getSquadIdx(self):
        return self._getNumber(9)

    def setSquadIdx(self, value):
        self._setNumber(9, value)

    def getIsPersonal(self):
        return self._getBool(10)

    def setIsPersonal(self, value):
        self._setBool(10, value)

    def getTeam(self):
        return self._getNumber(11)

    def setTeam(self, value):
        self._setNumber(11, value)

    def getIsSameSquad(self):
        return self._getBool(12)

    def setIsSameSquad(self, value):
        self._setBool(12, value)

    def getIdx(self):
        return self._getNumber(13)

    def setIdx(self, value):
        self._setNumber(13, value)

    def getVehicleCD(self):
        return self._getNumber(14)

    def setVehicleCD(self, value):
        self._setNumber(14, value)

    def getDbID(self):
        return self._getNumber(15)

    def setDbID(self, value):
        self._setNumber(15, value)

    def _initialize(self):
        super(PlayerModel, self)._initialize()
        self._addViewModelProperty('details', PlayerDetailsModel())
        self._addViewModelProperty('user', UserNameModel())
        self._addNumberProperty('earnedXp', 0)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('localizedVehicleName', '')
        self._addNumberProperty('kills', 0)
        self._addNumberProperty('damageDealt', 0)
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('vehicleLevel', 0)
        self._addNumberProperty('squadIdx', 0)
        self._addBoolProperty('isPersonal', False)
        self._addNumberProperty('team', 0)
        self._addBoolProperty('isSameSquad', False)
        self._addNumberProperty('idx', 0)
        self._addNumberProperty('vehicleCD', 0)
        self._addNumberProperty('dbID', 0)
