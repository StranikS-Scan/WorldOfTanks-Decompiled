# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/player_satisfaction_rating/player_satisfaction_widget.py
import logging
from constants import PlayerSatisfactionRating as RatingEnum
from gui.Scaleform.daapi.view.meta.PlayerSatisfactionWidgetMeta import PlayerSatisfactionWidgetMeta
from gui.Scaleform.genConsts.PLAYER_SATISFACTION_RATING import PLAYER_SATISFACTION_RATING
from gui.Scaleform.daapi.view.battle_results_window import IBattleResultsComponent
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

    def selectedChoice(self, choice):
        pass
