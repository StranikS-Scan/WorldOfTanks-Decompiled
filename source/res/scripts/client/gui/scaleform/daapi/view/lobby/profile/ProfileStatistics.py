# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileStatistics.py
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import BattleTypesDropDownItems, makeBattleTypesDropDown
from gui.Scaleform.daapi.view.lobby.profile.profile_statistics_vos import getStatisticsVO
from gui.Scaleform.daapi.view.lobby.profile.seasons_manager import makeStatisticsSeasonManagers
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
 PROFILE_DROPDOWN_KEYS.COMP7: 'comp7'}

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
        self.__seasonsManagers = makeStatisticsSeasonManagers()

    def setSeason(self, seasonId):
        if self.__seasonsManagers.setSeason(seasonId):
            self.as_updatePlayerStatsBtnS(self.__seasonsManagers.getPlayersStatsBtnEnabled())
            self.invokeUpdate()

    def showPlayersStats(self):
        self.__rankedController.showRankedBattlePage(ctx={'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID,
         'clientParams': {'spaID': self._databaseID}})

    def onCompletedSeasonsInfoChanged(self):
        self._setInitData()

    def requestDossier(self, bType):
        self.__seasonsManagers.onBattleTypeSwitched(bType)
        super(ProfileStatistics, self).requestDossier(bType)

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
        self.__seasonsManagers.clear()

    def _setInitData(self, accountDossier=None):
        self.as_setInitDataS({'dropDownProvider': makeBattleTypesDropDown(accountDossier)})

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
        self.__seasonsManagers.addSeasonsDropdown(vo)
        frameLabel = _FRAME_LABELS[self._battlesType]
        self.as_responseDossierS(self._battlesType, vo, frameLabel, '')
        return

    def _receiveFortDossier(self, accountDossier):
        return accountDossier.getFortSortiesStats()

    def _getNecessaryStats(self, accountDossier=None):
        if accountDossier is None:
            accountDossier = self.itemsCache.items.getAccountDossier(self._userID)
        seasonStats = self.__seasonsManagers.getStats(accountDossier)
        if seasonStats:
            return seasonStats
        else:
            return accountDossier.getSeasonRanked15x15Stats(RankedDossierKeys.ARCHIVE, ARCHIVE_SEASON_ID) if self._battlesType == PROFILE_DROPDOWN_KEYS.RANKED else super(ProfileStatistics, self)._getNecessaryStats(accountDossier)

    @classmethod
    def __updateStaticDropdownData(cls, vo):
        vo['showSeasonDropdown'] = True
        seasonItems = BattleTypesDropDownItems()
        seasonItems.addWithKeyAndLabel(PROFILE_DROPDOWN_KEYS.STATICTEAM, backport.text(R.strings.profile.profile.seasonsdropdown.all()))
        vo['seasonItems'] = seasonItems
        vo['seasonIndex'] = 0
        vo['seasonEnabled'] = False
