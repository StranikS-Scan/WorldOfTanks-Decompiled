# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileSection.py
from collections import namedtuple
from helpers import dependency, i18n
from gui.Scaleform.daapi.view.meta.ProfileSectionMeta import ProfileSectionMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from gui.Scaleform.daapi.view.lobby.comp7.comp7_profile_helper import COMP7_ARCHIVE_NAMES, COMP7_SEASON_NUMBERS, getDropdownKeyByArchiveName, getDropdownKeyBySeason
from stats_params import BATTLE_ROYALE_STATS_ENABLED
_DropdownData = namedtuple('_DropdownData', ('useSelf', 'funcName', 'params'))

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
        self.__battleTypeHandlers = {PROFILE_DROPDOWN_KEYS.ALL: _DropdownData(True, '_getTotalStatsBlock', {}),
         PROFILE_DROPDOWN_KEYS.TEAM: _DropdownData(False, 'getTeam7x7Stats', {}),
         PROFILE_DROPDOWN_KEYS.STATICTEAM: _DropdownData(False, 'getRated7x7Stats', {}),
         PROFILE_DROPDOWN_KEYS.HISTORICAL: _DropdownData(False, 'getHistoricalStats', {}),
         PROFILE_DROPDOWN_KEYS.FORTIFICATIONS: _DropdownData(True, '_receiveFortDossier', {}),
         PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_SORTIES: _DropdownData(False, 'getFortSortiesStats', {}),
         PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES: _DropdownData(False, 'getFortBattlesStats', {}),
         PROFILE_DROPDOWN_KEYS.COMPANY: _DropdownData(False, 'getCompanyStats', {}),
         PROFILE_DROPDOWN_KEYS.CLAN: _DropdownData(False, 'getGlobalMapStats', {}),
         PROFILE_DROPDOWN_KEYS.FALLOUT: _DropdownData(False, 'getFalloutStats', {}),
         PROFILE_DROPDOWN_KEYS.RANKED: _DropdownData(False, 'getRankedStats', {}),
         PROFILE_DROPDOWN_KEYS.RANKED_10X10: _DropdownData(False, 'getRanked10x10Stats', {}),
         PROFILE_DROPDOWN_KEYS.EPIC_RANDOM: _DropdownData(False, 'getEpicRandomStats', {}),
         PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO: _DropdownData(False, 'getBattleRoyaleSoloStats', {}),
         PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SQUAD: _DropdownData(False, 'getBattleRoyaleSquadStats', {})}
        for archiveName in COMP7_ARCHIVE_NAMES:
            dropdownKey = getDropdownKeyByArchiveName(archiveName)
            self.__battleTypeHandlers[dropdownKey] = _DropdownData(False, 'getComp7Stats', {'archive': archiveName})

        for season in COMP7_SEASON_NUMBERS:
            dropdownKey = getDropdownKeyBySeason(season)
            self.__battleTypeHandlers[dropdownKey] = _DropdownData(False, 'getComp7Stats', {'season': season})

    def __getData(self, battleType, obj):
        data = self.__battleTypeHandlers.get(battleType)
        if data is None:
            raise SoftException('ProfileSection: Unknown battle type: ' + self._battlesType)
        return getattr(self, data.funcName)(obj, **data.params) if data.useSelf else getattr(obj, data.funcName)(**data.params)

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

    def onSectionDeactivated(self):
        pass

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


class BattleTypesDropDownItems(list):

    def addByKey(self, key):
        self.addWithKeyAndLabel(key, i18n.makeString(PROFILE.profile_dropdown_labels(key)))

    def addWithKeyAndLabel(self, key, label):
        self.__addEntry(key, label)

    def __addEntry(self, key, label):
        self.append({'key': key,
         'label': label})


def makeBattleTypesDropDown(accountDossier, forVehiclesPage=False):
    dropDownProvider = BattleTypesDropDownItems()
    dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.ALL)
    dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.EPIC_RANDOM)
    if BATTLE_ROYALE_STATS_ENABLED:
        dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO)
        dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SQUAD)
    dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.RANKED)
    dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.RANKED_10X10)
    dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.FALLOUT)
    if accountDossier is not None and accountDossier.getHistoricalStats().getVehicles():
        dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.HISTORICAL)
    dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.TEAM)
    if accountDossier is not None and accountDossier.getRated7x7Stats().getVehicles():
        dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.STATICTEAM)
    dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.CLAN)
    if dependency.instance(ILobbyContext).getServerSettings().isStrongholdsEnabled():
        if forVehiclesPage:
            dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_SORTIES)
            dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.FORTIFICATIONS_BATTLES)
        else:
            dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.FORTIFICATIONS)
    dropDownProvider.addByKey(PROFILE_DROPDOWN_KEYS.COMP7)
    return dropDownProvider
