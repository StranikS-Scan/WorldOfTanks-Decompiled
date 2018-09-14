# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileSection.py
from gui.Scaleform.daapi.view.meta.ProfileSectionMeta import ProfileSectionMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.shared import g_itemsCache
from helpers import i18n

class ProfileSection(ProfileSectionMeta):

    def __init__(self, *args):
        super(ProfileSection, self).__init__()
        self.__isActive = False
        self._battlesType = PROFILE.PROFILE_DROPDOWN_LABELS_ALL
        self._userName = args[0]
        self._userID = args[1]
        self._databaseID = args[2]
        self._selectedData = args[3]
        self.__needUpdate = False

    def _populate(self):
        super(ProfileSection, self)._populate()
        self.requestDossier(self._battlesType)

    def requestDossier(self, bType):
        self._battlesType = bType
        self.invokeUpdate()

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
        if self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_ALL:
            data = self._getTotalStatsBlock(accountDossier)
        elif self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_TEAM:
            data = accountDossier.getTeam7x7Stats()
        elif self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_HISTORICAL:
            data = accountDossier.getHistoricalStats()
        elif self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_FORTIFICATIONS:
            data = self._receiveFortDossier(accountDossier)
        elif self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_FORTIFICATIONS_SORTIES:
            data = accountDossier.getFortSortiesStats()
        elif self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_FORTIFICATIONS_BATTLES:
            data = accountDossier.getFortBattlesStats()
        elif self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_COMPANY:
            data = accountDossier.getCompanyStats()
        elif self._battlesType == PROFILE.PROFILE_DROPDOWN_LABELS_CLAN:
            data = accountDossier.getClanStats()
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
