# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileSection.py
from helpers import dependency
from helpers import i18n
from gui.Scaleform.daapi.view.meta.ProfileSectionMeta import ProfileSectionMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException

class ProfileSection(ProfileSectionMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, *args):
        super(ProfileSection, self).__init__()
        self.__isActive = False
        self._battlesType = PROFILE_DROPDOWN_KEYS.ALL
        self._userName = args[0]
        self._userID = args[1]
        self._databaseID = args[2]
        self._selectedData = args[3]
        self._data = None
        self._dossier = None
        self.__needUpdate = False
        self.__battleTypeHandlers = {}
        self.__initHandlers()
        return

    def __initHandlers(self):
        self.__battleTypeHandlers = {PROFILE_DROPDOWN_KEYS.ALL: (True, '_getTotalStatsBlock'),
         PROFILE_DROPDOWN_KEYS.TEAM: (False, 'getTeam7x7Stats'),
         PROFILE_DROPDOWN_KEYS.STATICTEAM: (False, 'getRated7x7Stats'),
         PROFILE_DROPDOWN_KEYS.HISTORICAL: (False, 'getHistoricalStats'),
         PROFILE_DROPDOWN_KEYS.FORTIFICATIONS: (True, 'getHistoricalStats'),
         PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_SORTIES: (False, 'getFortSortiesStats'),
         PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES: (False, 'getFortBattlesStats'),
         PROFILE_DROPDOWN_KEYS.COMPANY: (False, 'getCompanyStats'),
         PROFILE_DROPDOWN_KEYS.CLAN: (False, 'getGlobalMapStats'),
         PROFILE_DROPDOWN_KEYS.FALLOUT: (False, 'getFalloutStats'),
         PROFILE_DROPDOWN_KEYS.RANKED: (False, 'getRankedStats'),
         PROFILE_DROPDOWN_KEYS.RANKED_10X10: (False, 'getRanked10x10Stats'),
         PROFILE_DROPDOWN_KEYS.EPIC_RANDOM: (False, 'getEpicRandomStats'),
         PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO: (False, 'getBattleRoyaleSoloStats'),
         PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SQUAD: (False, 'getBattleRoyaleSquadStats')}

    def __getData(self, battleType, obj):
        data = self.__battleTypeHandlers.get(battleType)
        if data is None:
            raise SoftException('ProfileSection: Unknown battle type: ' + self._battlesType)
        useSelf, funcName = data
        return getattr(self, funcName)(obj) if useSelf else getattr(obj, funcName)()

    def _populate(self):
        super(ProfileSection, self)._populate()
        self.requestDossier(self._battlesType)

    def _dispose(self):
        self._data = None
        self._dossier = None
        super(ProfileSection, self)._dispose()
        return

    def requestDossier(self, bType):
        self._battlesType = bType
        self.invokeUpdate()

    def onSectionActivated(self):
        pass

    def _dataProviderEntryAutoTranslate(self, key):
        return self._dataProviderEntry(key, i18n.makeString(PROFILE.profile_dropdown_labels(key)))

    @classmethod
    def _dataProviderEntry(cls, key, label):
        return {'key': key,
         'label': label}

    @classmethod
    def _getTotalStatsBlock(cls, dossier):
        return dossier.getRandomStats()

    def __receiveDossier(self):
        if self.__isActive and self.__needUpdate:
            self.__needUpdate = False
            accountDossier = self.itemsCache.items.getAccountDossier(self._userID)
            self._sendAccountData(self._getNecessaryStats(accountDossier), accountDossier)

    def _getNecessaryStats(self, accountDossier=None):
        if accountDossier is None:
            accountDossier = self.itemsCache.items.getAccountDossier(self._userID)
        data = self.__getData(self._battlesType, accountDossier)
        return data

    def _receiveFortDossier(self, accountDossier):
        return None

    def _sendAccountData(self, targetData, accountDossier):
        self._data = targetData
        self._dossier = accountDossier

    def setActive(self, value):
        self.__isActive = value
        self.__receiveDossier()

    def invokeUpdate(self):
        self._data = None
        self._dossier = None
        self.__needUpdate = True
        self.__receiveDossier()
        return

    @property
    def isActive(self):
        return self.__isActive

    def _formIconLabelInitObject(self, i18key, icon):
        return {'description': i18n.makeString(i18key),
         'icon': icon}
