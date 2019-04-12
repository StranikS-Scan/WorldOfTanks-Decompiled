# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_season_complete_view.py
import BigWorld
import SoundGroups
from SoundGroups import SoundGroups
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.meta.RankedBattlesSeasonCompleteViewMeta import RankedBattlesSeasonCompleteViewMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.constants import RankedDossierKeys
from gui.ranked_battles.ranked_builders import season_comple_vos
from gui.ranked_battles.ranked_formatters import getRanksColumnRewardsFormatter
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.bonuses import getBonuses
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.shared import IItemsCache
NOT_IN_LEAGE_ID = 0

class RankedBattlesSeasonCompleteView(RankedBattlesSeasonCompleteViewMeta):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(RankedBattlesSeasonCompleteView, self).__init__(ctx)
        self._soundsMap = {RANKEDBATTLES_ALIASES.SOUND_INFO_ANIMATION_START: '',
         RANKEDBATTLES_ALIASES.SOUND_AWARD_ANIMATION_START: '',
         RANKEDBATTLES_ALIASES.SOUND_BTN_ANIMATION_START: ''}
        if ctx is not None:
            self._quest = ctx['quest']
            self._awards = ctx['awards']
            self._closeCallback = ctx.get('closeClb', lambda : None)
        return

    def closeView(self):
        self.destroy()

    def onSoundTrigger(self, triggerName):
        soundName = self._soundsMap.get(triggerName, '')
        SoundGroups.g_instance.playSound2D(soundName)

    def showRating(self):
        self.__rankedController.showWebLeaguePage()
        self.destroy()

    def _populate(self):
        super(RankedBattlesSeasonCompleteView, self)._populate()
        self.__setData()

    def _dispose(self):
        super(RankedBattlesSeasonCompleteView, self)._dispose()
        self._closeCallback()

    def _packAwards(self):
        result = []
        formatter = getRanksColumnRewardsFormatter()
        for name, value in self._awards.iteritems():
            result.extend(formatter.getFormattedBonuses(getBonuses(self._quest, name, value), size=AWARDS_SIZES.BIG))

        return result

    def __setData(self):
        seasonID, league = ranked_helpers.getRankedDataFromTokenQuestID(self._quest.getID())
        season = self.__rankedController.getSeason(int(seasonID))
        if season is not None:
            leagueData = self.__rankedController.getLeagueProvider().webLeague
            if leagueData is not None and leagueData.position is not None:
                position = BigWorld.wg_getNiceNumberFormat(leagueData.position)
            else:
                position = '0'
            dossier = self.__itemsCache.items.getAccountDossier().getSeasonRankedStats(RankedDossierKeys.SEASON % season.getNumber(), seasonID)
            efficiency = dossier.getStepsEfficiency()
            efficiencyValue = efficiency * 100 if efficiency is not None else 0
            data = season_comple_vos.getFinishSeasonData(efficiencyValue, season)
            if league > NOT_IN_LEAGE_ID:
                data.update(season_comple_vos.getFinishInLeagueData(league, position))
                rewardData = season_comple_vos.getRewardData(self._packAwards())
            else:
                data.update(season_comple_vos.getFinishInDivisionsData(dossier.getAchievedRank()))
                rewardData = None
            self.as_setDataS(data)
            if rewardData:
                self.as_setRewardsDataS(rewardData)
        else:
            LOG_WARNING('Try to show RankedBattlesSeasonCompleteView, but season is None. Params: ', seasonID, league)
        return
