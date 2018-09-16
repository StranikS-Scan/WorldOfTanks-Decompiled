# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/RankedBattlesSeasonCompleteView.py
import BigWorld
from adisp import process
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.lobby.rankedBattles.finish_awards_view import FinishAwardsView
from gui.Scaleform.daapi.view.meta.RankedBattlesSeasonCompleteViewMeta import RankedBattlesSeasonCompleteViewMeta
from gui.Scaleform.genConsts.COMPONENTS_ALIASES import COMPONENTS_ALIASES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.ranked_battles import ranked_helpers
from helpers.i18n import makeString as _ms
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class RankedBattlesSeasonCompleteView(RankedBattlesSeasonCompleteViewMeta, FinishAwardsView):
    _INVISIBLE_AWARDS = ()

    def __init__(self, ctx=None):
        super(RankedBattlesSeasonCompleteView, self).__init__(ctx)
        FinishAwardsView.__init__(self, ctx)

    def closeView(self):
        self.destroy()

    def onSoundTrigger(self, triggerName):
        self._playSound(triggerName)

    def showRating(self):
        self.rankedController.openWebLeaguePage()
        self.destroy()

    def _populate(self):
        super(RankedBattlesSeasonCompleteView, self)._populate()
        self.__setData()

    def _dispose(self):
        super(RankedBattlesSeasonCompleteView, self)._dispose()
        self._closeCallback()

    @process
    def __setData(self):
        seasonID, cohort, _ = ranked_helpers.getRankedDataFromTokenQuestID(self._quest.getID())
        season = self.rankedController.getSeason(int(seasonID))
        if season is not None:
            leagueData = yield self.rankedController.getLeagueData()
            if leagueData is not None:
                position = BigWorld.wg_getNiceNumberFormat(leagueData['position'])
                league = leagueData.get('league', 0)
            else:
                position = '0'
                league = 0
            itemsCache = dependency.instance(IItemsCache)
            dossier = itemsCache.items.getAccountDossier().getPreviousSeasonRankedStats()
            seasonPoints = season.getPoints()
            efficiency = dossier.getStepsEfficiency()
            if efficiency is not None:
                efficiencyValue = efficiency * 100
            else:
                efficiencyValue = 0
            avgExp = dossier.getAvgXP()
            if avgExp is None:
                avgExp = 0
            self.as_setDataS({'leagueImage': RES_ICONS.getRankedWebLeagueIcon('big', league),
             'scoresValue': BigWorld.wg_getNiceNumberFormat(seasonPoints),
             'scoresLabel': _ms(RANKED_BATTLES.SEASONCOMPLETE_TOTALSCORES),
             'effectValue': BigWorld.wg_getIntegralFormat(efficiencyValue),
             'effectLabel': _ms(RANKED_BATTLES.SEASONCOMPLETE_EFFECTLABEL),
             'placeValue': position,
             'placeLabel': _ms(RANKED_BATTLES.SEASONCOMPLETE_PLACEINRATING),
             'expValue': BigWorld.wg_getIntegralFormat(avgExp),
             'expLabel': _ms(RANKED_BATTLES.SEASONCOMPLETE_EXPLABEL),
             'congratulationTitle': _ms(RANKED_BATTLES.SEASONCOMPLETE_BIGTITLE, season=str(season.getNumber())),
             'typeTitle': _ms(RANKED_BATTLES.SEASONCOMPLETE_SMALLTITLE),
             'typeIcon': RES_ICONS.MAPS_ICONS_BATTLETYPES_40X40_RANKED,
             'nextButtonLabel': _ms(RANKED_BATTLES.SEASONCOMPLETE_LEADERSBUTTON),
             'bgSource': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_BG_RANK_BLUR,
             'leagueLabel': _ms(RANKED_BATTLES.SEASONCOMPLETE_UNDERLABEL)})
            self.as_setRewardsDataS({'ribbonType': 'ribbon2',
             'rendererLinkage': COMPONENTS_ALIASES.RIBBON_AWARD_ANIM_RENDERER,
             'gap': 20,
             'rendererWidth': 80,
             'rendererHeight': 80,
             'awards': self._packAwards()})
        else:
            LOG_WARNING('Try to show RankedBattlesSeasonCompleteView, but season is None. Params: ', seasonID, cohort)
        return

    def _boxAnimationData(self):
        _, cohortNumber, _ = ranked_helpers.getRankedDataFromTokenQuestID(self._quest.getID())
        return ('metal', cohortNumber)
