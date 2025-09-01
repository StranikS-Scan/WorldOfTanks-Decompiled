# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/submodel_presenters/player_satisfaction.py
from typing import TYPE_CHECKING
import logging
from helpers import dependency
from gui.impl.gui_decorators import args2params
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from gui.impl.gen.view_models.views.lobby.battle_results.player_satisfaction_model import PlayerSatisfactionModel, PlayerSatisfactionStates
from constants import PlayerSatisfactionRating as RatingEnum
from player_satisfaction_schema import playerSatisfactionSchema
from skeletons.gui.battle_results import IBattleResultsService
if TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from typing import Type
    from gui.battle_results.stats_ctrl import BattleResults
_logger = logging.getLogger(__name__)
_RATING_TO_CHOICE_MAP = {RatingEnum.NONE: PlayerSatisfactionStates.NONE,
 RatingEnum.USUAL: PlayerSatisfactionStates.USUAL,
 RatingEnum.WORSE: PlayerSatisfactionStates.WORSE,
 RatingEnum.BETTER: PlayerSatisfactionStates.BETTER}
_CHOICE_TO_RATING_MAP = {choice:rating for rating, choice in _RATING_TO_CHOICE_MAP.iteritems()}

class PlayerSatisfactionSubPresenter(BattleResultsSubPresenter):
    __slots__ = ()
    __battleResults = dependency.descriptor(IBattleResultsService)

    @property
    def arenaUniqueId(self):
        return self.parentView.arenaUniqueID

    @property
    def viewModel(self):
        return self.getViewModel()

    @classmethod
    def getViewModelType(cls):
        return PlayerSatisfactionModel

    def _getEvents(self):
        events = [(self.viewModel.onSatisfactionRatingSelected, self.selectedChoice)]
        return events

    def packBattleResults(self, battleResults):
        hasBonusCap = battleResults.reusable.common.checkBonusCaps(ARENA_BONUS_TYPE_CAPS.PLAYER_SATISFACTION_RATING)
        config = playerSatisfactionSchema.getModel()
        isEnabled = hasBonusCap and config.enabledInterfaces.postbattle and config.enabled
        ratingFromBattle = self.__battleResults.getPlayerSatisfactionRating(self.arenaUniqueId)
        self.viewModel.setIsPlayerSatisfactionInterfaceEnabled(isEnabled)
        self.viewModel.setState(_RATING_TO_CHOICE_MAP.get(ratingFromBattle, PlayerSatisfactionStates.NONE))

    @args2params(PlayerSatisfactionStates)
    def selectedChoice(self, state):
        if self.arenaUniqueId is None:
            _logger.error('arenaUniqueID was not received when the parent view was registered.')
            return
        else:
            rating = _CHOICE_TO_RATING_MAP[state]
            self.__battleResults.submitPlayerSatisfactionRating(self.arenaUniqueId, rating)
            self.viewModel.setState(state)
            return
