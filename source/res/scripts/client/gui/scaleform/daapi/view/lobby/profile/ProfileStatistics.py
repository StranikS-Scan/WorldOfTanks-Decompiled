# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileStatistics.py
from collections import namedtuple
import constants
from debug_utils import LOG_ERROR
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.profile.profile_statistics_vos import getStatisticsVO
from gui.Scaleform.daapi.view.meta.ProfileStatisticsMeta import ProfileStatisticsMeta
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.ranked_battles.constants import RankedDossierKeys, ARCHIVE_SEASON_ID, SEASON_IDS_RB_2020
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from gui.Scaleform.genConsts.BATTLE_TYPES import BATTLE_TYPES
_RankedSeasonsKeys = namedtuple('_RankedSeasonsKeys', ['all', 'current', 'previous'])
_RANKED_SEASONS_ARCHIVE = 'archive'
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
 PROFILE_DROPDOWN_KEYS.RANKED_10X10: BATTLE_TYPES.RANKED_10X10}

def _packProviderType(mainType, addValue=None):
    return '%s/%s' % (mainType, str(addValue)) if addValue is not None else mainType


def _parseProviderType(value):
    return value.split('/')


class ProfileStatistics(ProfileStatisticsMeta):
    lobbyContext = dependency.descriptor(ILobbyContext)
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, *args):
        try:
            _, _, _, self.__ctx = args
        except Exception:
            LOG_ERROR('There is error while parsing profile stats page arguments', args)
            self.__ctx = {}

        super(ProfileStatistics, self).__init__(*args)
        seasonID = str(SEASON_IDS_RB_2020[-1])
        self.__rankedSeasonKey = _RANKED_SEASONS_ARCHIVE
        if seasonID is not None:
            self.__rankedSeasonKey = str(seasonID)
        return

    def requestDossier(self, bType):
        if bType == PROFILE_DROPDOWN_KEYS.RANKED_10X10:
            seasonID = self.__getLastActiveSeasonID()
            if seasonID is not None:
                self.__rankedSeasonKey = str(seasonID)
        elif bType == PROFILE_DROPDOWN_KEYS.RANKED:
            self.__rankedSeasonKey = str(SEASON_IDS_RB_2020[-1])
        super(ProfileStatistics, self).requestDossier(bType)
        return

    def setSeason(self, seasonId):
        if self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED:
            self.__rankedSeasonKey = seasonId
            self.as_updatePlayerStatsBtnS(self.__getPlayersStatsBtnEnabled())
            self.invokeUpdate()

    def showPlayersStats(self):
        self.rankedController.showRankedBattlePage(ctx={'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID,
         'clientParams': {'spaID': self._databaseID}})

    def onCompletedSeasonsInfoChanged(self):
        self._setInitData()

    def _populate(self):
        super(ProfileStatistics, self)._populate()
        self._setInitData()

    def _setInitData(self, accountDossier=None):
        dropDownProvider = [self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.ALL),
         self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.EPIC_RANDOM),
         self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.RANKED),
         self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.RANKED_10X10),
         self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FALLOUT)]
        if accountDossier is not None and accountDossier.getHistoricalStats().getVehicles():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.HISTORICAL))
        dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.TEAM))
        if accountDossier is not None and accountDossier.getRated7x7Stats().getVehicles():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.STATICTEAM))
        dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.CLAN))
        if self.lobbyContext.getServerSettings().isStrongholdsEnabled():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FORTIFICATIONS))
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
            vo['playersStats'] = self.__getPlayersStatsBtnEnabled()
            if self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED_10X10:
                vo['testText'] = backport.text(R.strings.ranked_battles.rankedBattleMainView.season(), season=backport.text(R.strings.ranked_battles.rankedBattleMainView.seasonName()))
            if self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED:
                self.__updateRankedDropdownData(vo, self.__rankedSeasonKey)
        self.as_responseDossierS(self._battlesType, vo, _FRAME_LABELS[self._battlesType], '')
        return

    def _receiveFortDossier(self, accountDossier):
        return accountDossier.getFortSortiesStats()

    def _getNecessaryStats(self, accountDossier=None):
        if accountDossier is None:
            accountDossier = self.itemsCache.items.getAccountDossier(self._userID)
        if self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED:
            return self._getRanked15x15Stats(accountDossier)
        else:
            return self._getRanked10x10Stats(accountDossier) if self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED_10X10 else super(ProfileStatistics, self)._getNecessaryStats(accountDossier)

    def _getRanked10x10Stats(self, accountDossier):
        return accountDossier.getRanked10x10Stats()

    def _getRanked15x15Stats(self, accountDossier):
        result = None
        if self.__rankedSeasonKey == _RANKED_SEASONS_ARCHIVE:
            result = accountDossier.getSeasonRanked15x15Stats(RankedDossierKeys.ARCHIVE, ARCHIVE_SEASON_ID)
        else:
            seasonID = int(self.__rankedSeasonKey)
            if seasonID in SEASON_IDS_RB_2020:
                seasonKey = RankedDossierKeys.SEASON % (SEASON_IDS_RB_2020.index(seasonID) + 1)
                result = accountDossier.getSeasonRanked15x15Stats(seasonKey, seasonID)
        return result

    @classmethod
    def __updateStaticDropdownData(cls, vo):
        vo['showSeasonDropdown'] = True
        vo['seasonItems'] = [cls._dataProviderEntry(PROFILE_DROPDOWN_KEYS.STATICTEAM, backport.text(R.strings.profile.profile.seasonsdropdown.all()))]
        vo['seasonIndex'] = 0
        vo['seasonEnabled'] = False

    def __updateRankedDropdownData(self, vo, selectedLabel):
        showDropDown = vo['showSeasonDropdown'] = self.__hasRankedSeasonsHistory()
        if showDropDown:
            seasonItems = vo['seasonItems'] = [self._dataProviderEntry(_RANKED_SEASONS_ARCHIVE, backport.text(R.strings.profile.profile.ranked.seasonsdropdown.archive()))]
            seasonIds = SEASON_IDS_RB_2020
            seasonNumber = 1
            for seasonID in seasonIds:
                seasonsDropdownRes = R.strings.profile.profile.ranked.seasonsdropdown
                seasonsdropdown = seasonsDropdownRes.dyn(constants.CURRENT_REALM, seasonsDropdownRes)
                seasonItems.append(self._dataProviderEntry(str(seasonID), backport.text(seasonsdropdown.num(seasonNumber)())))
                seasonNumber += 1

            seasonIndex = len(seasonItems) - 1
            for i, seasonItem in enumerate(seasonItems):
                if seasonItem['key'] == selectedLabel:
                    seasonIndex = i

            vo['seasonIndex'] = seasonIndex
            vo['seasonEnabled'] = True

    def __hasRankedSeasonsHistory(self):
        passedSeasons = len(self.rankedController.getSeasonPassed())
        return passedSeasons >= 1 or self.rankedController.getCurrentSeason() is not None

    def __getLastActiveSeasonID(self):
        currentSeason = self.rankedController.getCurrentSeason()
        if currentSeason:
            statsSeasonID = currentSeason.getSeasonID()
        else:
            seasons = self.rankedController.getSeasonPassed()
            seasons.sort()
            hasSeasons = bool(len(seasons))
            statsSeasonID = seasons[-1][0] if hasSeasons else None
        return statsSeasonID

    def __getPlayersStatsBtnEnabled(self):
        result = self.rankedController.isEnabled()
        if result:
            statsSeasonID = self.__getLastActiveSeasonID()
            result = str(statsSeasonID) == self.__rankedSeasonKey if statsSeasonID is not None else False
        return result
