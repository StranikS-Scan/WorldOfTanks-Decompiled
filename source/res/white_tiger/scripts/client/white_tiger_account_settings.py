# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger_account_settings.py
from account_helpers.AccountSettings import KEY_SETTINGS, KEY_NOTIFICATIONS, DEFAULT_VALUES
from events_core_client.account_settings import AccountEventSettingsHandler
from wt_settings import g_wt_config
WT_ACCOUNT_SETTINGS_KEY = 'WhiteTiger'
WTA_EXPIRY_DATE_KEY = 'expiryDate'
WTA_IS_INTRO_VIEWED_KEY = 'isIntroVideoViewed'
WTA_IS_OUTRO_VIDEO_VIEWED_KEY = 'isOutroVideoViewed'
WTA_SAVED_VEHICLE_CD_KEY = 'savedVehCD'
WTA_SAVED_HUNTER_VEHICLE_CD_KEY = 'savedHunterVehCD'
WTA_SAVED_BOSS_VEHICLE_CD_KEY = 'savedBossVehCD'
WTA_BOSS_BATTLE_COUNT_KEY = 'bossBattleCount'
WTA_HUNTER_BATTLE_COUNT_KEY = 'hunterBattleCount'
WTA_DEFAULT_SETTINGS = {WTA_IS_INTRO_VIEWED_KEY: False,
 WTA_IS_OUTRO_VIDEO_VIEWED_KEY: False,
 WTA_BOSS_BATTLE_COUNT_KEY: 0,
 WTA_HUNTER_BATTLE_COUNT_KEY: 0,
 WTA_SAVED_VEHICLE_CD_KEY: None,
 WTA_SAVED_HUNTER_VEHICLE_CD_KEY: None,
 WTA_SAVED_BOSS_VEHICLE_CD_KEY: None}

class WTAccountSettings(object):

    def __init__(self, eventController):
        self.__accSettings = AccountEventSettingsHandler(WT_ACCOUNT_SETTINGS_KEY, WTA_EXPIRY_DATE_KEY, eventController)

    def init(self):
        DEFAULT_VALUES[KEY_SETTINGS].setdefault(WT_ACCOUNT_SETTINGS_KEY, WTA_DEFAULT_SETTINGS)
        DEFAULT_VALUES[KEY_NOTIFICATIONS].setdefault(WT_ACCOUNT_SETTINGS_KEY, WTA_DEFAULT_SETTINGS)

    def migrateAccount(self):
        self.__accSettings.migrateAccount()

    def setIntroViewed(self, status):
        self.__accSettings.setSetting(WTA_IS_INTRO_VIEWED_KEY, status)

    def setOutroVideoViewed(self, status):
        self.__accSettings.setSetting(WTA_IS_OUTRO_VIDEO_VIEWED_KEY, status)

    def saveVehicleCD(self, vehicleCD):
        if vehicleCD not in g_wt_config.getAllVehiclesData():
            return
        if g_wt_config.isHunterVehicle(vehicleCD):
            self.__accSettings.setSetting(WTA_SAVED_HUNTER_VEHICLE_CD_KEY, vehicleCD)
        elif g_wt_config.isBossVehicle(vehicleCD):
            self.__accSettings.setSetting(WTA_SAVED_BOSS_VEHICLE_CD_KEY, vehicleCD)
        self.__accSettings.setSetting(WTA_SAVED_VEHICLE_CD_KEY, vehicleCD)

    def increaseBossBattleCount(self):
        self.__accSettings.setSetting(WTA_BOSS_BATTLE_COUNT_KEY, self.bossBattleCount + 1)

    def increaseHunterBattleCount(self):
        self.__accSettings.setSetting(WTA_HUNTER_BATTLE_COUNT_KEY, self.hunterBattleCount + 1)

    @property
    def isIntroViewed(self):
        return self.__accSettings.settings.get(WTA_IS_INTRO_VIEWED_KEY)

    @property
    def isOutroVideoViewed(self):
        return self.__accSettings.settings.get(WTA_IS_OUTRO_VIDEO_VIEWED_KEY)

    @property
    def savedVehicleCD(self):
        return self.__accSettings.settings.get(WTA_SAVED_VEHICLE_CD_KEY)

    @property
    def savedHunterVehicleCD(self):
        return self.__accSettings.settings.get(WTA_SAVED_HUNTER_VEHICLE_CD_KEY)

    @property
    def savedBossVehicleCD(self):
        return self.__accSettings.settings.get(WTA_SAVED_BOSS_VEHICLE_CD_KEY)

    @property
    def bossBattleCount(self):
        return self.__accSettings.settings.get(WTA_BOSS_BATTLE_COUNT_KEY)

    @property
    def hunterBattleCount(self):
        return self.__accSettings.settings.get(WTA_HUNTER_BATTLE_COUNT_KEY)

    @property
    def settings(self):
        return self.__accSettings.settings
