# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/player_satisfaction_rating/player_satisfaction_widget.py
import logging
from constants import PlayerSatisfactionRating as RatingEnum
from gui.Scaleform.daapi.view.meta.PlayerSatisfactionWidgetMeta import PlayerSatisfactionWidgetMeta
from gui.Scaleform.genConsts.PLAYER_SATISFACTION_RATING import PLAYER_SATISFACTION_RATING
from gui.Scaleform.daapi.view.battle_results_window import IBattleResultsComponent
from gui.impl.common.player_satisfaction_rating.player_satisfaction_sound import playSoundForRating
from gui.impl.common.player_satisfaction_rating.randomize_feedback import SELECTION_ORDER, getFeedbackMsgID
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
_logger = logging.getLogger(__name__)
_RATING_TO_CHOICE_MAP = {RatingEnum.NONE: PLAYER_SATISFACTION_RATING.NONE,
 RatingEnum.USUAL: PLAYER_SATISFACTION_RATING.USUAL,
 RatingEnum.WORSE: PLAYER_SATISFACTION_RATING.WORSE,
 RatingEnum.BETTER: PLAYER_SATISFACTION_RATING.BETTER}
_CHOICE_TO_RATING_MAP = {choice:rating for rating, choice in _RATING_TO_CHOICE_MAP.iteritems()}

class PlayerSatisfactionWidget(PlayerSatisfactionWidgetMeta, IBattleResultsComponent):
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self):
        super(PlayerSatisfactionWidget, self).__init__()
        self._arenaUniqueID = None
        return

    def setArenaUniqueID(self, arenaUniqueID):
        self._arenaUniqueID = arenaUniqueID
        self.updateChoiceState()

    def updateChoiceState(self):
        ratingFromBattle = self.__battleResults.getPlayerSatisfactionRating(self._arenaUniqueID)
        choices, feedback = buildChoiceAndFeedbackData(SELECTION_ORDER, self._arenaUniqueID)
        self.as_setInitDataS(choices, feedback, _RATING_TO_CHOICE_MAP[ratingFromBattle])

    def selectedChoice(self, choice):
        if self._arenaUniqueID is None:
            _logger.error('arenaUniqueID was not received when component was registered.')
            return
        else:
            rating = _CHOICE_TO_RATING_MAP[choice]
            self.__battleResults.submitPlayerSatisfactionRating(self._arenaUniqueID, rating)
            playSoundForRating(rating)
            return


def buildChoiceAndFeedbackData(ratingOrder, arenaUniqueID):
    choices = []
    feedback = []
    for ratingVariant in ratingOrder:
        choices.append(_RATING_TO_CHOICE_MAP[ratingVariant])
        feedback.append(getFeedbackMsgID(ratingVariant, arenaUniqueID))

    return (choices, feedback)
