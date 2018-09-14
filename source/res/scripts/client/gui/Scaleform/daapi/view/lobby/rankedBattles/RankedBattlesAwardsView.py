# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/RankedBattlesAwardsView.py
import SoundGroups
from gui.Scaleform.daapi.view.meta.RankedBattlesAwardsViewMeta import RankedBattlesAwardsViewMeta
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.ranked_battles.constants import RANK_TYPES, SOUND
from gui.shared.formatters import text_styles
from helpers import i18n, dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedBattlesAwardsView(RankedBattlesAwardsViewMeta):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx=None):
        super(RankedBattlesAwardsView, self).__init__()
        assert 'rankID' in ctx
        self.__rankID = ctx['rankID']
        self.__showNext = ctx.get('showNext', True)
        self.__vehicle = ctx.get('vehicle')

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
        self.rankedController.setAwardWindowShown(self.__rankID)
        rank = self.rankedController.getRank(self.__rankID, vehicle=self.__vehicle)
        isAccountMastered = self.rankedController.isAccountMastered()
        isCurrentRankMaster = rank.getType() == RANK_TYPES.VEHICLE
        rankVOs = {'currentRank': {'rankTitle': RANKED_BATTLES.AWARDS_GOTRANK,
                         'rank': {'imageSrc': rank.getIcon('huge'),
                                  'smallImageSrc': None,
                                  'isEnabled': True,
                                  'isMaster': isCurrentRankMaster,
                                  'rankID': str(self.__rankID),
                                  'rankCount': 'x{}'.format(rank.getSerialID()) if isCurrentRankMaster else ''},
                         'congratulationTitle': RANKED_BATTLES.AWARDS_CONGRATULATION,
                         'scoresTitle': text_styles.highlightText(i18n.makeString(RANKED_BATTLES.AWARDS_NEXTRANKTITLE, scores=text_styles.promoSubTitle(rank.getPoints()))),
                         'nextButtonLabel': RANKED_BATTLES.AWARDS_NEXT if isAccountMastered else RANKED_BATTLES.AWARDS_YES,
                         'awards': rank.getAwardsVOs(iconSize='big')}}
        if isAccountMastered and self.__showNext:
            nextRankID = self.__rankID + 1
            nextRank = self.rankedController.getRank(nextRankID, vehicle=self.__vehicle)
            stagesCount = nextRank.getStepsCountToAchieve()
            rankVOs['nextRank'] = {'rank': {'imageSrc': nextRank.getIcon('huge'),
                      'smallImageSrc': None,
                      'isEnabled': True,
                      'isMaster': True,
                      'rankID': str(nextRank.getID()),
                      'rankCount': ''},
             'stagesCount': stagesCount,
             'congratulationTitle': RANKED_BATTLES.AWARDS_CONGRATULATION,
             'scoresTitle': text_styles.highlightText(i18n.makeString(RANKED_BATTLES.AWARDS_STAGESTITLE, stage=text_styles.bonusLocalText(stagesCount))),
             'nextButtonLabel': RANKED_BATTLES.AWARDS_YES}
        self.as_setDataS(rankVOs)
        rankID = 'max' if isCurrentRankMaster else self.__rankID
        SoundGroups.g_instance.playSound2D(SOUND.getRankAwardAnimationEvent(rankID))
        return

    def _dispose(self):
        super(RankedBattlesAwardsView, self)._dispose()

    def __close(self):
        self.destroy()
