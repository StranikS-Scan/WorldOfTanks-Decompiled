# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileSection.py
from helpers import i18n
from gui.clubs.ClubsController import g_clubsCtrl
from gui.Scaleform.daapi.view.meta.ProfileSectionMeta import ProfileSectionMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.LobbyContext import g_lobbyContext
from gui.shared import g_itemsCache
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS

class ProfileSection(ProfileSectionMeta):

    def __init__(self, *args):
        super(ProfileSection, self).__init__()
        self.__isActive = False
        self._battlesType = PROFILE_DROPDOWN_KEYS.ALL
        self._userName = args[0]
        self._userID = args[1]
        self._databaseID = args[2]
        self._selectedData = args[3]
        self._seasonID = None
        self.__needUpdate = False
        return

    def _populate(self):
        super(ProfileSection, self)._populate()
        self.requestDossier(self._battlesType)

    def requestDossier(self, bType):
        self._battlesType = bType
        self.invokeUpdate()

    def setSeasonID(self, battleType, seasonID = None):
        self._battlesType = battleType
        self._seasonID = seasonID
        self.invokeUpdate()

    def _dataProviderEntryAutoTranslate(self, key):
        return self._dataProviderEntry(key, i18n.makeString(PROFILE.profile_dropdown_labels(key)))

    def _dataProviderEntry(self, key, label):
        return {'key': key,
         'label': label}

    @classmethod
    def _getTotalStatsBlock(cls, dossier):
        return dossier.getRandomStats()

    def __receiveDossier(self):
        if self.__isActive and self.__needUpdate:
            self.__needUpdate = False
            accountDossier = g_itemsCache.items.getAccountDossier(self._userID)
            self._sendAccountData(self._getNecessaryStats(accountDossier), accountDossier)

    def _getNecessaryStats(self, accountDossier = None):
        if accountDossier is None:
            accountDossier = g_itemsCache.items.getAccountDossier(self._userID)
        if self._battlesType == PROFILE_DROPDOWN_KEYS.ALL:
            data = self._getTotalStatsBlock(accountDossier)
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.TEAM:
            data = accountDossier.getTeam7x7Stats()
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.STATICTEAM:
            if self._seasonID is not None:
                data = accountDossier.getSeasonRated7x7Stats(int(self._seasonID))
            else:
                data = accountDossier.getRated7x7Stats()
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.STATICTEAM_SEASON:
            currentSeasonID = g_lobbyContext.getServerSettings().eSportCurrentSeason.getID()
            data = accountDossier.getSeasonRated7x7Stats(currentSeasonID)
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.HISTORICAL:
            data = accountDossier.getHistoricalStats()
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.FORTIFICATIONS:
            data = self._receiveFortDossier(accountDossier)
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_SORTIES:
            data = accountDossier.getFortSortiesStats()
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES:
            data = accountDossier.getFortBattlesStats()
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.COMPANY:
            data = accountDossier.getCompanyStats()
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.CLAN:
            data = accountDossier.getGlobalMapStats()
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.FALLOUT:
            data = accountDossier.getFalloutStats()
        else:
            raise ValueError('ProfileSection: Unknown battle type: ' + self._battlesType)
        return data

    def _receiveFortDossier(self, accountDossier):
        return None

    def _sendAccountData(self, targetData, accountDossier):
        pass

    def setActive(self, value):
        self.__isActive = value
        self.__receiveDossier()

    def invokeUpdate(self):
        self.__needUpdate = True
        self.__receiveDossier()

    @property
    def isActive(self):
        return self.__isActive

    def _formIconLabelInitObject(self, i18key, icon):
        return {'description': i18n.makeString(i18key),
         'icon': icon}
