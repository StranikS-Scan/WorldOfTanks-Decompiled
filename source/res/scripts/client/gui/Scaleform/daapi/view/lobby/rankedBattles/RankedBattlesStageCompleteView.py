# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/RankedBattlesStageCompleteView.py
from gui.Scaleform.daapi.view.lobby.rankedBattles.finish_awards_view import FinishAwardsView
from gui.Scaleform.daapi.view.meta.RankedBattlesStageCompleteViewMeta import RankedBattlesStageCompleteViewMeta
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.money import Currency
from helpers import i18n
from shared_utils import first

class RankedBattlesStageCompleteView(RankedBattlesStageCompleteViewMeta, FinishAwardsView):

    def __init__(self, ctx=None):
        super(RankedBattlesStageCompleteView, self).__init__(ctx)
        FinishAwardsView.__init__(self, ctx)
        self.__season = ctx['season']

    def closeView(self):
        self.destroy()

    def onSoundTrigger(self, triggerName):
        self._playSound(triggerName)

    def _populate(self):
        super(RankedBattlesStageCompleteView, self)._populate()
        if self.__season is not None:
            cycle = self.__season.getAllCycles()[self._quest.getCycleID()]
            rank = self.rankedController.getRank(self._quest.getRank())
            try:
                proxy_currency_count = first(self._quest.getBonuses(Currency.CRYSTAL)).getValue()
            except AttributeError:
                proxy_currency_count = 0

            self.as_setDataS({'rank': {'imageSrc': rank.getIcon('small'),
                      'smallImageSrc': None,
                      'isEnabled': True,
                      'isMaster': False,
                      'rankID': str(rank.getID())},
             'boxImage': rank.getBoxIcon(),
             'bestRankTitle': RANKED_BATTLES.SEASONCOMPLETE_BESTRANK,
             'proxyCurrency': text_styles.highTitle(i18n.makeString(RANKED_BATTLES.SEASONCOMPLETE_PROXYCURRENCY, value=text_styles.superPromoTitle(proxy_currency_count))),
             'scoresTitle': text_styles.highlightText(i18n.makeString(RANKED_BATTLES.SEASONCOMPLETE_SCORESEARNED, scores=text_styles.bonusLocalText(cycle.points))),
             'congratulationTitle': i18n.makeString(RANKED_BATTLES.SEASONCOMPLETE_STAGECOMPLETE, stage=cycle.ordinalNumber),
             'nextButtonLabel': RANKED_BATTLES.AWARDS_YES,
             'bgSource': RES_ICONS.MAPS_ICONS_RANKEDBATTLES_BG_RANK_BLUR})
            self.as_setRewardsDataS({'ribbonType': 'ribbon2',
             'rendererLinkage': 'RibbonAwardAnimUI',
             'gap': 20,
             'rendererWidth': 80,
             'rendererHeight': 80,
             'awards': self._packAwards()})
        return

    def _dispose(self):
        super(RankedBattlesStageCompleteView, self)._dispose()
        self._closeCallback()

    def _boxAnimationData(self):
        return ('wood', self._quest.getRank())
