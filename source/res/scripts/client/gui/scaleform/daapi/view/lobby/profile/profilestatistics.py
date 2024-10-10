# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileStatistics.py
from collections import namedtuple
from debug_utils import LOG_ERROR
from stats_params import BATTLE_ROYALE_STATS_ENABLED
from gui.Scaleform.daapi.view.lobby.profile.profile_statistics_vos import getStatisticsVO
from gui.Scaleform.daapi.view.meta.ProfileStatisticsMeta import ProfileStatisticsMeta
from gui.Scaleform.genConsts.BATTLE_TYPES import BATTLE_TYPES
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.constants import RankedDossierKeys, ARCHIVE_SEASON_ID
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import ProfileStatisticEvent
from gui.shared import g_eventBus
from gui.Scaleform.daapi.view.lobby.comp7.comp7_profile_helper import COMP7_ARCHIVE_NAMES, COMP7_SEASON_NUMBERS, isComp7Archive, isComp7Season, getDropdownKeyByArchiveName, getDropdownKeyBySeason
_RankedSeasonsKeys = namedtuple('_RankedSeasonsKeys', ['all', 'current', 'previous'])
_RANKED_SEASONS_ARCHIVE = 'archive'
RANKED_SEASONS_ARCHIVE_10x10 = '_10x10'
_FRAME_LABELS = {PROFILE_DROPDOWN_KEYS.ALL: 'random',
 PROFILE_DROPDOWN_KEYS.EPIC_RANDOM: 'epicRandom',
 PROFILE_DROPDOWN_KEYS.FALLOUT: 'fallout',
 PROFILE_DROPDOWN_KEYS.HISTORICAL: 'historical',
 PROFILE_DROPDOWN_KEYS.TEAM: 'team7x7',
 PROFILE_DROPDOWN_KEYS.STATICTEAM: 'team7x7',
 PROFILE_DROPDOWN_KEYS.CLAN: 'clan',
 PROFILE_DROPDOWN_KEYS.FORTIFICATIONS: 'fortifications',
 PROFILE_DROPDOWN_KEYS.STATICTEAM_SEASON: 'team7x7',
 PROFILE_DROPDOWN_KEYS.RANKED: 'ranked_15x15',
 PROFILE_DROPDOWN_KEYS.RANKED_10X10: BATTLE_TYPES.RANKED_10X10,
 PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO: 'battle_royale',
 PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SQUAD: 'battle_royale',
 PROFILE_DROPDOWN_KEYS.VERSUS_AI: 'versusAI'}
_COMP7_FRAME_LABEL = 'comp7'

def _packProviderType(mainType, addValue=None):
    return '%s/%s' % (mainType, str(addValue)) if addValue is not None else mainType


def _parseProviderType(value):
    return value.split('/')


class ProfileStatistics(ProfileStatisticsMeta):
    lobbyContext = dependency.descriptor(ILobbyContext)
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, *args):
        try:
            _, _, _, self.__ctx = args
        except Exception:
            LOG_ERROR('There is error while parsing profile stats page arguments', args)
            self.__ctx = {}

        super(ProfileStatistics, self).__init__(*args)
        self.__seasonsManagers = self.__initSeasonsManagers()

    def setSeason(self, seasonId):
        if self.__getSeasonsManager().setSeason(seasonId):
            self.as_updatePlayerStatsBtnS(self.__getSeasonsManager().getPlayersStatsBtnEnabled())
            self.invokeUpdate()

    def showPlayersStats(self):
        self.__rankedController.showRankedBattlePage(ctx={'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID,
         'clientParams': {'spaID': self._databaseID}})

    def onCompletedSeasonsInfoChanged(self):
        self._setInitData()

    def _populate(self):
        event = ProfileStatisticEvent(ProfileStatisticEvent.SELECT_BATTLE_TYPE)
        if self._selectedData and isinstance(self._selectedData, dict):
            event.ctx['eventOwner'] = self._selectedData.get('eventOwner')
        else:
            event.ctx['eventOwner'] = 'achievements'
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)
        self._battlesType = event.ctx.get('battlesType', self._battlesType)
        super(ProfileStatistics, self)._populate()
        self._setInitData()

    def _dispose(self):
        super(ProfileStatistics, self)._dispose()
        g_eventBus.handleEvent(ProfileStatisticEvent(ProfileStatisticEvent.DISPOSE), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__clearSeasonsManagers()

    def _setInitData(self, accountDossier=None):
        dropDownProvider = [self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.ALL), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.EPIC_RANDOM)]
        if BATTLE_ROYALE_STATS_ENABLED:
            dropDownProvider += [self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SQUAD)]
        dropDownProvider += [self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.RANKED), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.RANKED_10X10), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FALLOUT)]
        if accountDossier is not None and accountDossier.getHistoricalStats().getVehicles():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.HISTORICAL))
        dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.TEAM))
        if accountDossier is not None and accountDossier.getRated7x7Stats().getVehicles():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.STATICTEAM))
        dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.CLAN))
        if self.lobbyContext.getServerSettings().isStrongholdsEnabled():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FORTIFICATIONS))
        for archive in COMP7_ARCHIVE_NAMES:
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(getDropdownKeyByArchiveName(archive)))

        dropDownProvider += [self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.VERSUS_AI)]
        for season in COMP7_SEASON_NUMBERS:
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(getDropdownKeyBySeason(season)))

        self.as_setInitDataS({'dropDownProvider': dropDownProvider})
        return

    def _sendAccountData(self, targetData, accountDossier):
        super(ProfileStatistics, self)._sendAccountData(targetData, accountDossier)
        self._setInitData(accountDossier)
        vo = getStatisticsVO(battlesType=self._battlesType, targetData=targetData, accountDossier=accountDossier, isCurrentUser=self._userID is None)
        if self._battlesType == PROFILE_DROPDOWN_KEYS.TEAM:
            vo['showSeasonDropdown'] = False
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.STATICTEAM or self._battlesType == PROFILE_DROPDOWN_KEYS.STATICTEAM_SEASON:
            self._battlesType = PROFILE_DROPDOWN_KEYS.STATICTEAM
            vo['headerText'] = backport.text(R.strings.profile.section.statistics.headerText.staticTeam())
            vo['dropdownSeasonLabel'] = text_styles.main(backport.text(R.strings.cyberSport.StaticFormationStatsView.seasonFilter()))
            self.__updateStaticDropdownData(vo)
        elif self._battlesType in (PROFILE_DROPDOWN_KEYS.RANKED, PROFILE_DROPDOWN_KEYS.RANKED_10X10):
            vo['seasonDropdownAttachToTitle'] = True
            vo['playersStatsLbl'] = backport.text(R.strings.ranked_battles.statistic.playersRaiting())
        self.__getSeasonsManager().addSeasonsDropdown(vo)
        if isComp7Season(self._battlesType) or isComp7Archive(self._battlesType):
            frameLabel = _COMP7_FRAME_LABEL
        else:
            frameLabel = _FRAME_LABELS[self._battlesType]
        self.as_responseDossierS(self._battlesType, vo, frameLabel, '')
        return

    def _receiveFortDossier(self, accountDossier):
        return accountDossier.getFortSortiesStats()

    def _getNecessaryStats(self, accountDossier=None):
        if accountDossier is None:
            accountDossier = self.itemsCache.items.getAccountDossier(self._userID)
        seasonStats = self.__getSeasonsManager().getStats(accountDossier)
        if seasonStats:
            return seasonStats
        else:
            return accountDossier.getSeasonRanked15x15Stats(RankedDossierKeys.ARCHIVE, ARCHIVE_SEASON_ID) if self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED else super(ProfileStatistics, self)._getNecessaryStats(accountDossier)

    def __initSeasonsManagers(self):
        return {'default': _BaseSeasonManager(),
         PROFILE_DROPDOWN_KEYS.RANKED_10X10: _RankedSeasonsManager(self._dataProviderEntry)}

    def __getSeasonsManager(self):
        return self.__seasonsManagers[self._battlesType] if self._battlesType in self.__seasonsManagers else self.__seasonsManagers['default']

    def __clearSeasonsManagers(self):
        for manager in self.__seasonsManagers.values():
            manager.clear()

        self.__seasonsManagers = {}

    @classmethod
    def __updateStaticDropdownData(cls, vo):
        vo['showSeasonDropdown'] = True
        vo['seasonItems'] = [cls._dataProviderEntry(PROFILE_DROPDOWN_KEYS.STATICTEAM, backport.text(R.strings.profile.profile.seasonsdropdown.all()))]
        vo['seasonIndex'] = 0
        vo['seasonEnabled'] = False


class _BaseSeasonManager(object):

    def __init__(self, entryFactory=None):
        self._entryFactory = entryFactory
        self._seasonKey = None
        return

    def clear(self):
        self._entryFactory = None
        return

    def setSeason(self, seasonId):
        if self._seasonKey == seasonId:
            return False
        self._seasonKey = seasonId
        return True

    def addSeasonsDropdown(self, targetVO):
        pass

    def getPlayersStatsBtnEnabled(self):
        return False

    def getStats(self, accountDossier):
        return None


class _RankedSeasonsManager(_BaseSeasonManager):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def addSeasonsDropdown(self, targetVO):
        targetVO['showSeasonDropdown'] = False
        targetVO['playersStats'] = False

    def getStats(self, accountDossier):
        return accountDossier.getSeasonRankedStats(RANKED_SEASONS_ARCHIVE_10x10, 0)
