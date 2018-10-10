# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/finish_awards_view.py
import SoundGroups
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.ranked_battles.constants import SOUND
from gui.server_events.bonuses import getBonuses
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from gui.shared.money import Currency

class FinishAwardsView(object):
    _INVISIBLE_AWARDS = (Currency.CRYSTAL,)
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx=None):
        super(FinishAwardsView, self).__init__()
        self._soundsMap = {RANKEDBATTLES_ALIASES.SOUND_INFO_ANIMATION_START: SOUND.SEASON_RESULT_ANIMATION_START,
         RANKEDBATTLES_ALIASES.SOUND_AWARD_ANIMATION_START: SOUND.SEASON_RESULT_AWARD_ANIMATION,
         RANKEDBATTLES_ALIASES.SOUND_BTN_ANIMATION_START: SOUND.SEASON_RESULT_BUTTON_ANIMATION}
        if ctx is not None:
            self._quest = ctx['quest']
            self._awards = ctx['awards']
            self._closeCallback = ctx.get('closeClb', lambda : None)
        return

    def _packAwards(self):
        result = []
        for name, value in self._awards.iteritems():
            if name not in self._INVISIBLE_AWARDS:
                for bonus in getBonuses(self._quest, name, value):
                    result.extend(bonus.getRankedAwardVOs('big'))

        return result

    def _playSound(self, triggerName):
        if triggerName == RANKEDBATTLES_ALIASES.SOUND_BOX_ANIMATION_START:
            soundName = SOUND.getBoxAnimationEvent(*self._boxAnimationData())
        else:
            soundName = self._soundsMap[triggerName]
        SoundGroups.g_instance.playSound2D(soundName)

    def _boxAnimationData(self):
        raise NotImplementedError
