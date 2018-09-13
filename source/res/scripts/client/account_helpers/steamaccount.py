# Embedded file name: scripts/client/account_helpers/SteamAccount.py
import BigWorld
import constants
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG
STEAM_IS_DEVELOPMENT = constants.IS_DEVELOPMENT
STEAM_SUPPORT = False

class __SteamAccount(object):
    _GET_USER_INFO_URL = 'https://api.steampowered.com/ISteamMicroTxn/GetUserInfo/V0001/?steamid=%d'
    _STEAM_LOGIN_SUFFIX = '@steam.com'

    def __init__(self):
        self.userInfo = None
        return

    @property
    def isValid(self):
        return STEAM_SUPPORT and BigWorld.wg_isSteamInitialized()

    @property
    def steamID(self):
        raise self.isValid or AssertionError('Available only for steam users')
        return BigWorld.wg_getSteamID()

    def getCredentials(self):
        raise self.isValid or AssertionError('Available only for steam users')
        user = ('%d@steam.dev' if STEAM_IS_DEVELOPMENT else self._STEAM_LOGIN_SUFFIX) % self.steamID
        password = '' if STEAM_IS_DEVELOPMENT else BigWorld.wg_getSteamAuthTicket()
        return (user, password)


g_steamAccount = __SteamAccount()
