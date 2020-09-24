# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_season_complete_view.py
import logging
import SoundGroups
from gui.Scaleform.daapi.view.meta.RankedBattlesSeasonCompleteViewMeta import RankedBattlesSeasonCompleteViewMeta
from gui.impl import backport
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.constants import RankedDossierKeys
from gui.ranked_battles.ranked_builders import season_comple_vos
from gui.ranked_battles.ranked_formatters import getRankedAwardsFormatter
from gui.ranked_battles.ranked_helpers.web_season_provider import UNDEFINED_LEAGUE_ID
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.bonuses import getBonuses
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class RankedBattlesSeasonCompleteView(RankedBattlesSeasonCompleteViewMeta):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(RankedBattlesSeasonCompleteView, self).__init__(ctx)
        ctx = ctx or {}
        self._quest = ctx.get('quest')
        self._awards = ctx.get('awards')

    def closeView(self):
        self.destroy()

    def onSoundTrigger(self, soundName):
        SoundGroups.g_instance.playSound2D(soundName)

    def showRating(self):
        self.__rankedController.showRankedBattlePage(ctx={'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RATING_ID})
        self.destroy()

    def _populate(self):
        super(RankedBattlesSeasonCompleteView, self)._populate()
        self.__rankedController.getSoundManager().setOverlayStateOn()
        self.__rankedController.getWebSeasonProvider().onInfoUpdated += self.__updatePosition
        if self._quest is not None and self._awards is not None:
            self.__setData()
        else:
            logging.error('Wrong ctx! Quest and awards must be defined!')
        return

    def _dispose(self):
        self.__rankedController.getWebSeasonProvider().onInfoUpdated -= self.__updatePosition
        self.__rankedController.getSoundManager().setOverlayStateOff()
        super(RankedBattlesSeasonCompleteView, self)._dispose()

    def __getPosition(self):
        webSeasonInfo = self.__rankedController.getWebSeasonProvider().seasonInfo
        if webSeasonInfo.league == UNDEFINED_LEAGUE_ID:
            webSeasonInfo = self.__rankedController.getClientSeasonInfo()
        return backport.getNiceNumberFormat(webSeasonInfo.position) if webSeasonInfo.position else '0'

    def __packAwards(self):
        result = []
        formatter = getRankedAwardsFormatter()
        for name, value in self._awards.iteritems():
            result.extend(formatter.getFormattedBonuses(getBonuses(self._quest, name, value), size=AWARDS_SIZES.BIG))

        return result

    def __setData(self):
        seasonID, league, isSprinter = ranked_helpers.getDataFromSeasonTokenQuestID(self._quest.getID())
        season = self.__rankedController.getSeason(seasonID)
        if season is not None:
            awardsData = None
            seasonNumber = season.getNumber()
            dossierKey = RankedDossierKeys.SEASON % seasonNumber
            dossier = self.__itemsCache.items.getAccountDossier().getSeasonRankedStats(dossierKey, seasonID)
            efficiency = dossier.getStepsEfficiency()
            position = self.__getPosition()
            efficiencyValue = efficiency * 100 if efficiency is not None else 0.0
            data = season_comple_vos.getFinishSeasonData(efficiencyValue, seasonNumber)
            if league > UNDEFINED_LEAGUE_ID:
                data.update(season_comple_vos.getFinishInLeagueData(league, position, seasonNumber, isSprinter))
                awardsData = season_comple_vos.getAwardsData(self.__packAwards())
            else:
                rankID = dossier.getAchievedRank()
                division = self.__rankedController.getDivision(rankID)
                data.update(season_comple_vos.getFinishInDivisionsData(division, rankID, seasonNumber))
            self.as_setDataS(data)
            if awardsData:
                self.as_setAwardsDataS(awardsData)
        else:
            _logger.warning('Try to show RankedBattlesSeasonCompleteView, but season is None. Params: %s %s', seasonID, league)
        return

    def __updatePosition(self):
        self.as_setPlaceS(self.__getPosition())
