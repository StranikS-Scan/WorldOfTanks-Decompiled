# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/battle_player.py
from enum import Enum
from gui.impl.gen import R
from gui.impl.gen.view_models.common.commendationStateModel import CommendationStateModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeEmblemModel

class VehicleTypeEnum(Enum):
    ATSPG = 'atSpg'
    HEAVYTANK = 'heavyTank'
    LIGHTTANK = 'lightTank'
    MEDIUMTANK = 'mediumTank'
    SPG = 'spg'
    UNDEFINED = 'undefined'


class BattlePlayer(UserNameModel):
    __slots__ = ()

    def __init__(self, properties=37, commands=0):
        super(BattlePlayer, self).__init__(properties=properties, commands=commands)

    @property
    def prestigeEmblemModel(self):
        return self._getViewModel(10)

    @staticmethod
    def getPrestigeEmblemModelType():
        return PrestigeEmblemModel

    @property
    def commendationStateModel(self):
        return self._getViewModel(11)

    @staticmethod
    def getCommendationStateModelType():
        return CommendationStateModel

    def getIsCurrentPlayer(self):
        return self._getBool(12)

    def setIsCurrentPlayer(self, value):
        self._setBool(12, value)

    def getVehicleId(self):
        return self._getNumber(13)

    def setVehicleId(self, value):
        self._setNumber(13, value)

    def getAvatarSessionID(self):
        return self._getString(14)

    def setAvatarSessionID(self, value):
        self._setString(14, value)

    def getPlatoon(self):
        return self._getNumber(15)

    def setPlatoon(self, value):
        self._setNumber(15, value)

    def getIsMyPlatoon(self):
        return self._getBool(16)

    def setIsMyPlatoon(self, value):
        self._setBool(16, value)

    def getIsInviteSent(self):
        return self._getBool(17)

    def setIsInviteSent(self, value):
        self._setBool(17, value)

    def getIsInviteReceived(self):
        return self._getBool(18)

    def setIsInviteReceived(self, value):
        self._setBool(18, value)

    def getIsPlatoonInvitationDisabled(self):
        return self._getBool(19)

    def setIsPlatoonInvitationDisabled(self, value):
        self._setBool(19, value)

    def getKills(self):
        return self._getNumber(20)

    def setKills(self, value):
        self._setNumber(20, value)

    def getVehicleName(self):
        return self._getString(21)

    def setVehicleName(self, value):
        self._setString(21, value)

    def getIsChatMuted(self):
        return self._getBool(22)

    def setIsChatMuted(self, value):
        self._setBool(22, value)

    def getIsVoiceMuted(self):
        return self._getBool(23)

    def setIsVoiceMuted(self, value):
        self._setBool(23, value)

    def getIsVoiceActive(self):
        return self._getBool(24)

    def setIsVoiceActive(self, value):
        self._setBool(24, value)

    def getVehicleContourUrl(self):
        return self._getString(25)

    def setVehicleContourUrl(self, value):
        self._setString(25, value)

    def getVehicleType(self):
        return VehicleTypeEnum(self._getString(26))

    def setVehicleType(self, value):
        self._setString(26, value.value)

    def getVehicleLevel(self):
        return self._getNumber(27)

    def setVehicleLevel(self, value):
        self._setNumber(27, value)

    def getIsKiller(self):
        return self._getBool(28)

    def setIsKiller(self, value):
        self._setBool(28, value)

    def getIsReported(self):
        return self._getBool(29)

    def setIsReported(self, value):
        self._setBool(29, value)

    def getIsLoaded(self):
        return self._getBool(30)

    def setIsLoaded(self, value):
        self._setBool(30, value)

    def getAnonymizerTooltip(self):
        return self._getString(31)

    def setAnonymizerTooltip(self, value):
        self._setString(31, value)

    def getLiveTagTooltipTitle(self):
        return self._getResource(32)

    def setLiveTagTooltipTitle(self, value):
        self._setResource(32, value)

    def getLiveTagTooltipBody(self):
        return self._getResource(33)

    def setLiveTagTooltipBody(self, value):
        self._setResource(33, value)

    def getLiveTagDamage(self):
        return self._getBool(34)

    def setLiveTagDamage(self, value):
        self._setBool(34, value)

    def getLiveTagAssist(self):
        return self._getBool(35)

    def setLiveTagAssist(self, value):
        self._setBool(35, value)

    def getLiveTagBlock(self):
        return self._getBool(36)

    def setLiveTagBlock(self, value):
        self._setBool(36, value)

    def _initialize(self):
        super(BattlePlayer, self)._initialize()
        self._addViewModelProperty('prestigeEmblemModel', PrestigeEmblemModel())
        self._addViewModelProperty('commendationStateModel', CommendationStateModel())
        self._addBoolProperty('isCurrentPlayer', False)
        self._addNumberProperty('vehicleId', 0)
        self._addStringProperty('avatarSessionID', '')
        self._addNumberProperty('platoon', 0)
        self._addBoolProperty('isMyPlatoon', False)
        self._addBoolProperty('isInviteSent', False)
        self._addBoolProperty('isInviteReceived', False)
        self._addBoolProperty('isPlatoonInvitationDisabled', False)
        self._addNumberProperty('kills', 0)
        self._addStringProperty('vehicleName', '')
        self._addBoolProperty('isChatMuted', False)
        self._addBoolProperty('isVoiceMuted', False)
        self._addBoolProperty('isVoiceActive', False)
        self._addStringProperty('vehicleContourUrl', '')
        self._addStringProperty('vehicleType', VehicleTypeEnum.UNDEFINED.value)
        self._addNumberProperty('vehicleLevel', 0)
        self._addBoolProperty('isKiller', False)
        self._addBoolProperty('isReported', False)
        self._addBoolProperty('isLoaded', False)
        self._addStringProperty('anonymizerTooltip', '')
        self._addResourceProperty('liveTagTooltipTitle', R.invalid())
        self._addResourceProperty('liveTagTooltipBody', R.invalid())
        self._addBoolProperty('liveTagDamage', False)
        self._addBoolProperty('liveTagAssist', False)
        self._addBoolProperty('liveTagBlock', False)
