# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/RankedBattlesAwardsView.py
import SoundGroups
from gui.Scaleform.daapi.view.meta.RankedBattlesAwardsViewMeta import RankedBattlesAwardsViewMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.ranked_battles.constants import RANK_TYPES, SOUND
from gui.ranked_battles.ranked_helpers import buildRankVO
from gui.shared.formatters import text_styles
from helpers import i18n, dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedBattlesAwardsView(RankedBattlesAwardsViewMeta):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx=None):
        super(RankedBattlesAwardsView, self).__init__()
        self.__rankID = ctx['rankID']
        self.__vehicle = ctx.get('vehicle')
        self.__awards = ctx.get('awards')
        self.__isDebug = ctx.get('isDebug', False)

    def onEscapePress(self):
        self.__close()

    def onWindowClose(self):
        self.destroy()

    def closeView(self):
        self.__close()

    def onSoundTrigger(self, triggerName):
        SoundGroups.g_instance.playSound2D(triggerName)

    def _populate(self):
        super(RankedBattlesAwardsView, self)._populate()
        if not self.__isDebug:
            self.rankedController.setAwardWindowShown(self.__rankID)
        rank = self.rankedController.getRank(self.__rankID, vehicle=self.__vehicle)
        if rank.getType() == RANK_TYPES.VEHICLE:
            points = self.rankedController.getLadderPoints()
            scoreTitle = RANKED_BATTLES.AWARDS_LADDERPOINTSTOTAL
            rankID = 'max'
            rankTitle = RANKED_BATTLES.AWARDS_GOTLADDERPOINT
        else:
            points = rank.getPoints()
            scoreTitle = RANKED_BATTLES.AWARDS_NEXTRANKTITLE
            rankID = self.__rankID
            rankTitle = i18n.makeString(RANKED_BATTLES.AWARDS_GOTRANK, rank=rankID)
        rankVOs = {'currentRank': {'rankTitle': rankTitle,
                         'rank': buildRankVO(rank=rank, imageSize=RANKEDBATTLES_ALIASES.WIDGET_HUGE, isEnabled=True, shieldStatus=self.rankedController.getShieldStatus(rank)),
                         'congratulationTitle': RANKED_BATTLES.AWARDS_CONGRATULATION,
                         'scoresTitle': text_styles.highlightText(i18n.makeString(scoreTitle, scores=text_styles.promoSubTitle(points))),
                         'nextButtonLabel': RANKED_BATTLES.AWARDS_YES,
                         'awards': self.__getAllReceivedAwards()}}
        self.as_setDataS(rankVOs)
        SoundGroups.g_instance.playSound2D(SOUND.getRankAwardAnimationEvent(rankID))

    def __getAllReceivedAwards(self):
        if self.__awards is not None:
            return self.__awards
        else:
            rank = self.rankedController.getRank(self.__rankID, vehicle=self.__vehicle)
            return rank.getAwardsVOs(iconSize='big')

    def __close(self):
        self.destroy()
