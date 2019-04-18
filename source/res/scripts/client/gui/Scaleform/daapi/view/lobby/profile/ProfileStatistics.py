# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileStatistics.py
from collections import namedtuple
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.profile.profile_statistics_vos import getStatisticsVO
from gui.Scaleform.daapi.view.meta.ProfileStatisticsMeta import ProfileStatisticsMeta
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.ranked_battles.constants import RankedDossierKeys, ARCHIVE_SEASON_ID
from gui.shared.formatters import text_styles
from helpers import i18n, dependency
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext
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
 PROFILE_DROPDOWN_KEYS.RANKED: 'ranked'}

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
        season = self.rankedController.getCurrentSeason()
        self.__rankedSeasonKey = _RANKED_SEASONS_ARCHIVE
        if season:
            self.__rankedSeasonKey = str(season.getSeasonID())

    def setSeason(self, seasonId):
        if self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED:
            self.__rankedSeasonKey = seasonId
            self.invokeUpdate()

    def onCompletedSeasonsInfoChanged(self):
        self._setInitData()

    def _populate(self):
        super(ProfileStatistics, self)._populate()
        self._setInitData()

    def _setInitData(self, accountDossier=None):
        dropDownProvider = [self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.ALL),
         self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.EPIC_RANDOM),
         self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.RANKED),
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
            vo['headerText'] = i18n.makeString(PROFILE.SECTION_STATISTICS_HEADERTEXT_STATICTEAM)
            vo['dropdownSeasonLabel'] = text_styles.main(CYBERSPORT.STATICFORMATIONSTATSVIEW_SEASONFILTER)
            self.__updateStaticDropdownData(vo)
        elif self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED:
            vo['seasonDropdownAttachToTitle'] = True
            vo['playersStatsLbl'] = i18n.makeString(RANKED_BATTLES.STATISTIC_PLAYERSRAITING)
            vo['playersStats'] = self.rankedController.isEnabled()
            self.__updateRankedDropdownData(vo, self.__rankedSeasonKey)
        self.as_responseDossierS(self._battlesType, vo, _FRAME_LABELS[self._battlesType], '')
        return

    def _receiveFortDossier(self, accountDossier):
        return accountDossier.getFortSortiesStats()

    def _getNecessaryStats(self, accountDossier=None):
        if self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED:
            if accountDossier is None:
                accountDossier = self.itemsCache.items.getAccountDossier(self._userID)
            if self.__rankedSeasonKey == _RANKED_SEASONS_ARCHIVE:
                return accountDossier.getSeasonRankedStats(RankedDossierKeys.ARCHIVE, ARCHIVE_SEASON_ID)
            season = self.rankedController.getSeason(int(self.__rankedSeasonKey))
            if season:
                seasonKey = RankedDossierKeys.SEASON % season.getNumber()
                seasonID = season.getSeasonID()
                return accountDossier.getSeasonRankedStats(seasonKey, seasonID)
        return super(ProfileStatistics, self)._getNecessaryStats(accountDossier)

    @classmethod
    def __updateStaticDropdownData(cls, vo):
        vo['showSeasonDropdown'] = True
        vo['seasonItems'] = [cls._dataProviderEntry(PROFILE_DROPDOWN_KEYS.STATICTEAM, PROFILE.PROFILE_SEASONSDROPDOWN_ALL)]
        vo['seasonIndex'] = 0
        vo['seasonEnabled'] = False

    def __updateRankedDropdownData(self, vo, selectedLabel):
        showDropDown = vo['showSeasonDropdown'] = self.__hasRankedSeasonsHistory()
        if showDropDown:
            seasonItems = vo['seasonItems'] = [self._dataProviderEntry(_RANKED_SEASONS_ARCHIVE, PROFILE.get_ranked_season_lbl(_RANKED_SEASONS_ARCHIVE))]
            seasonIndex = 0
            sortedSeasons = sorted(self.rankedController.getSeasonPassed(), key=lambda seasonData: seasonData[1])
            seasonIds = [ seasonID for seasonID, _ in sortedSeasons ]
            currentSeason = self.rankedController.getCurrentSeason()
            if currentSeason:
                seasonIds.append(currentSeason.getSeasonID())
            for seasonID in seasonIds:
                season = self.rankedController.getSeason(seasonID)
                if season:
                    seasonItems.append(self._dataProviderEntry(str(seasonID), PROFILE.get_ranked_season_lbl(str(season.getNumber()))))

            for i, seasonItem in enumerate(seasonItems):
                if seasonItem['key'] == selectedLabel:
                    seasonIndex = i

            vo['seasonIndex'] = seasonIndex
            vo['seasonEnabled'] = True

    def __hasRankedSeasonsHistory(self):
        passedSeasons = len(self.rankedController.getSeasonPassed())
        return passedSeasons >= 1 or self.rankedController.getCurrentSeason() is not None

    def showPlayersStats(self):
        self.rankedController.showRankedBattlePage(ctx={'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID})
