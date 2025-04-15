# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/player_format.py
from collections import namedtuple
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class _FORMAT_MASK(object):
    NONE = 0
    NAME = 1
    VEHICLE = 2
    CLAN = 4
    REGION = 8
    NAME_VEHICLE = NAME | VEHICLE
    NAME_CLAN = NAME | CLAN
    NAME_VEH_CLAN = NAME | VEHICLE | CLAN
    NAME_REGION = NAME | REGION
    NAME_VEH_REGION = NAME | VEHICLE | REGION
    NAME_REG_CLAN = NAME | CLAN | REGION
    ALL = NAME | VEHICLE | CLAN | REGION


_PLAYER_FULL_NAME_FORMATS = {_FORMAT_MASK.VEHICLE: u'{2:>s}',
 _FORMAT_MASK.NAME_VEHICLE: u'{0:>s} ({2:>s})',
 _FORMAT_MASK.NAME_CLAN: u'{0:>s}[{1:>s}]',
 _FORMAT_MASK.NAME_VEH_CLAN: u'{0:>s}[{1:>s}] ({2:>s})',
 _FORMAT_MASK.NAME_REGION: u'{0:>s} {3:>s}',
 _FORMAT_MASK.NAME_VEH_REGION: u'{0:>s} {3:>s} ({2:>s})',
 _FORMAT_MASK.NAME_REG_CLAN: u'{0:>s}[{1:>s}] {3:>s}',
 _FORMAT_MASK.ALL: u'{0:>s}[{1:>s}] {3:>s} ({2:>s})'}
PlayerFormatResult = namedtuple('PlayerFormatResult', ('playerFullName', 'playerName', 'playerFakeName', 'clanAbbrev', 'regionCode', 'vehicleName'))

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getRegionCode(accountDBID, lobbyContext=None):
    regionCode = None
    if lobbyContext is not None:
        serverSettings = lobbyContext.getServerSettings()
        if serverSettings is not None:
            roaming = serverSettings.roaming
            if accountDBID and not roaming.isSameRealm(accountDBID):
                _, regionCode = roaming.getPlayerHome(accountDBID)
    return regionCode


class PlayerFullNameFormatter(object):

    def __init__(self):
        super(PlayerFullNameFormatter, self).__init__()
        self.__isVehicleShortNameShown = False
        self.__isClanShown = True
        self.__isRegionShown = True
        self.__isPlayerNameShown = True

    @classmethod
    def create(cls, isVehicleShortNameShown=True, isClanShown=True, isRegionShown=True):
        formatter = cls()
        formatter.setVehicleShortNameShown(isVehicleShortNameShown)
        formatter.setClanShown(isClanShown)
        formatter.setRegionShown(isRegionShown)
        return formatter

    def setVehicleShortNameShown(self, flag):
        self.__isVehicleShortNameShown = flag

    def setClanShown(self, flag):
        self.__isClanShown = flag

    def setRegionShown(self, flag):
        self.__isRegionShown = flag

    def setPlayerNameShown(self, flag):
        self.__isPlayerNameShown = flag

    def format(self, vInfoVO, playerName=None):
        key = _FORMAT_MASK.NONE
        vehShortName = ''
        vehName = ''
        regionCode = ''
        vehType = vInfoVO.vehicleType
        if vehType is not None:
            if self.__isVehicleShortNameShown:
                vehName = vehShortName = vehType.shortNameWithPrefix
                key |= _FORMAT_MASK.VEHICLE
            else:
                vehName = vehType.name
        if self.__isPlayerNameShown:
            key |= _FORMAT_MASK.NAME
        if playerName is None:
            playerName = self._normalizePlayerName(vInfoVO.player.getPlayerLabel())
        fakePlayerName = vInfoVO.player.getPlayerFakeLabel()
        clanAbbrev = ''
        if self.__isClanShown:
            clanAbbrev = vInfoVO.player.clanAbbrev
            if clanAbbrev:
                key |= _FORMAT_MASK.CLAN
        if self.__isRegionShown:
            regionCode = getRegionCode(vInfoVO.player.accountDBID)
            if regionCode:
                key |= _FORMAT_MASK.REGION
        if key == _FORMAT_MASK.NONE:
            fullName = playerName
        else:
            fullName = _PLAYER_FULL_NAME_FORMATS.get(key, u'{0:>s}').format(playerName, clanAbbrev, vehShortName, regionCode)
        return PlayerFormatResult(fullName, playerName, fakePlayerName, clanAbbrev, regionCode, vehName)

    @staticmethod
    def _normalizePlayerName(name):
        return name
