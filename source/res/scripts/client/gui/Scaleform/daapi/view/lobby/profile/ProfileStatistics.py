# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileStatistics.py
from collections import namedtuple
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.profile.profile_statistics_vos import getStatisticsVO
from gui.Scaleform.daapi.view.meta.ProfileStatisticsMeta import ProfileStatisticsMeta
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.shared.formatters import text_styles
from helpers import i18n, dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IRankedBattlesController
_RankedSeasonsKeys = namedtuple('_RankedSeasonsKeys', ['all', 'current', 'previous'])
_RANKED_SEASONS_KEYS = _RankedSeasonsKeys('all', 'current', 'previous')
_FRAME_LABELS = {PROFILE_DROPDOWN_KEYS.ALL: 'random',
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
        self.__rankedSeason = _RANKED_SEASONS_KEYS.all

    def setSeason(self, seasonId):
        if self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED:
            self.__rankedSeason = seasonId
            self.invokeUpdate()

    def onCompletedSeasonsInfoChanged(self):
        self._setInitData()

    def _populate(self):
        super(ProfileStatistics, self)._populate()
        self._setInitData()

    def _setInitData(self, accountDossier=None):
        dropDownProvider = [self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.ALL), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.RANKED), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.FALLOUT)]
        if accountDossier is not None and accountDossier.getHistoricalStats().getVehicles():
            dropDownProvider.append(self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.HISTORICAL))
        dropDownProvider.extend((self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.TEAM), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.STATICTEAM), self._dataProviderEntryAutoTranslate(PROFILE_DROPDOWN_KEYS.CLAN)))
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
            vo['playersStats'] = True
            self.__updateRankedDropdownData(vo, self.__rankedSeason)
        self.as_responseDossierS(self._battlesType, vo, _FRAME_LABELS[self._battlesType], '')
        return

    def _receiveFortDossier(self, accountDossier):
        return accountDossier.getFortSortiesStats()

    def _getNecessaryStats(self, accountDossier=None):
        if self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED:
            if accountDossier is None:
                accountDossier = self.itemsCache.items.getAccountDossier(self._userID)
            if self.__rankedSeason == _RANKED_SEASONS_KEYS.current:
                return accountDossier.getCurrentSeasonRankedStats()
            if self.__rankedSeason == _RANKED_SEASONS_KEYS.previous:
                return accountDossier.getPreviousSeasonRankedStats()
            if self.__rankedSeason == _RANKED_SEASONS_KEYS.all:
                return accountDossier.getRankedStats()
        return super(ProfileStatistics, self)._getNecessaryStats(accountDossier)

    @classmethod
    def __updateStaticDropdownData(cls, vo):
        vo['showSeasonDropdown'] = True
        vo['seasonItems'] = [cls._dataProviderEntry(PROFILE_DROPDOWN_KEYS.STATICTEAM, PROFILE.PROFILE_SEASONSDROPDOWN_ALL)]
        vo['seasonIndex'] = 0
        vo['seasonEnabled'] = False

    def __updateRankedDropdownData(self, vo, currentSeason):
        showDropDown = vo['showSeasonDropdown'] = self.__hasRankedSeasonsHistory()
        if showDropDown:
            seasonItems = vo['seasonItems'] = []
            seasonIndex = 0
            for i, item in enumerate(_RANKED_SEASONS_KEYS):
                if currentSeason == item:
                    seasonIndex = i
                seasonItems.append(self._dataProviderEntry(item, PROFILE.get_ranked_season_lbl(item)))

            vo['seasonIndex'] = seasonIndex
            vo['seasonEnabled'] = True

    def __hasRankedSeasonsHistory(self):
        """
        We have the ranked history only in two cases:
        1) The number of passed seasons >= 2
        2) The number of passed seasons == 1 and there is an active current Season
        :return: boolean result
        """
        passedSeasons = len(self.rankedController.getSeasonPassed())
        return passedSeasons > 1 or passedSeasons == 1 and self.rankedController.getCurrentSeason() is not None

    def showPlayersStats(self):
        self.rankedController.openWebLeaguePage()
