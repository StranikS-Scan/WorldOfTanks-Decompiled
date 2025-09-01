# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/postmortem_panel/postmortem_panel_view.py
import logging
import typing
import BigWorld
from PlayerEvents import g_playerEvents
from aih_constants import CTRL_MODE_NAME
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_TYPE
from constants import ARENA_GUI_TYPE, PlayerSatisfactionRating
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.postmorten_panel.postmortem_info_panel_view_model import PostmortemInfoPanelViewModel
from gui.impl.gen.view_models.views.battle.postmorten_panel.rating_button_model import RateButtonEnum
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl
from gui.shared.events import DeathCamEvent
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
from gui.impl.common.player_satisfaction_rating.player_satisfaction_sound import playSoundForRating
from player_satisfaction_schema import playerSatisfactionSchema
if typing.TYPE_CHECKING:
    from typing import Tuple, Optional, Callable
    from Event import Event
    from constants import FINISH_REASON
_logger = logging.getLogger(__name__)
_MODEL_TO_COMMON_ENUM_MAP = {RateButtonEnum.WORSE: PlayerSatisfactionRating.WORSE,
 RateButtonEnum.USUAL: PlayerSatisfactionRating.USUAL,
 RateButtonEnum.BETTER: PlayerSatisfactionRating.BETTER,
 RateButtonEnum.UNSET: PlayerSatisfactionRating.NONE}
SELECTION_ORDER = (PlayerSatisfactionRating.NONE,
 PlayerSatisfactionRating.WORSE,
 PlayerSatisfactionRating.USUAL,
 PlayerSatisfactionRating.BETTER)
_COMMON_TO_MODEL_ENUM_MAP = {v:k for k, v in _MODEL_TO_COMMON_ENUM_MAP.iteritems()}

class PostmortemPanelView(ViewImpl, CallbackDelayer):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __BLINK_DURATION = 5

    def __init__(self):
        viewSettings = ViewSettings(R.views.battle.postmortem_panel.PostmortemPanelView(), ViewFlags.VIEW, PostmortemInfoPanelViewModel())
        super(PostmortemPanelView, self).__init__(viewSettings)

    @property
    def viewModel(self):
        return super(PostmortemPanelView, self).getViewModel()

    @property
    def isRatingWidgetEnabled(self):
        bonusTypeVistor = self.sessionProvider.arenaVisitor.bonus
        hasBonusCap = bonusTypeVistor.hasBonusCap(BONUS_TYPE.PLAYER_SATISFACTION_RATING)
        config = playerSatisfactionSchema.getModel()
        return hasBonusCap and config.enabledInterfaces.spectatorMode and config.enabled if config else False

    def _getEvents(self):
        events = [(self.viewModel.onRateButtonClick, self.__onRateButtonClick), (g_playerEvents.onRoundFinished, self._onRoundFinished)]
        killCamCtrl = self.sessionProvider.shared.killCamCtrl
        if killCamCtrl:
            events.append((killCamCtrl.onKillCamModeStateChanged, self.__onKillCamStateChanged))
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            events.append((ctrl.onPostMortemSwitched, self.__onPostMortemSwitched))
        return tuple(events)

    def _initialize(self, *args, **kwargs):
        super(PostmortemPanelView, self)._initialize()
        with self.viewModel.transaction() as model:
            model.setIsRatingWidgetEnabled(self.isRatingWidgetEnabled)
            self._setButtonConfig(model)
            isFrontline = self.sessionProvider.arenaVisitor.getArenaGuiType() in ARENA_GUI_TYPE.EPIC_RANGE
            model.setIsFrontline(isFrontline)
            isFreeCamAvailable = avatar_getter.isPostmortemFeatureEnabled(CTRL_MODE_NAME.DEATH_FREE_CAM)
            model.setIsFreecamAvailable(isFreeCamAvailable)

    def _finalize(self):
        super(PostmortemPanelView, self)._finalize()
        self.stopCallback(self.__stopHint)

    def __onPostMortemSwitched(self, _, respawnAvailable):
        self.__startHint()
        if self.sessionProvider.arenaVisitor.getArenaGuiType() in ARENA_GUI_TYPE.EPIC_RANGE:
            self.viewModel.setHasLivesAvailable(respawnAvailable)

    def __onKillCamStateChanged(self, state, _):
        if state is DeathCamEvent.State.FINISHED:
            self.__startHint()

    def __startHint(self):
        self.viewModel.setIsBlinking(True)
        self.delayCallback(self.__BLINK_DURATION, self.__stopHint)

    def __stopHint(self):
        self.viewModel.setIsBlinking(False)

    @args2params(RateButtonEnum)
    def __onRateButtonClick(self, rating):
        rating = _MODEL_TO_COMMON_ENUM_MAP.get(rating, PlayerSatisfactionRating.NONE)
        if rating is PlayerSatisfactionRating.NONE:
            _logger.warning('Received unmappable rating from widget callback: %s', rating)
            return
        playSoundForRating(rating)
        BigWorld.player().cell.submitPlayerSatisfactionRating(rating)

    def _onRoundFinished(self, winnerTeam, reason):
        self.viewModel.setIsRatingWidgetVisible(False)

    def _setButtonConfig(self, model):
        buttonArray = model.getRatingButtons()
        buttonArray.clear()
        buttonArray.reserve(len(RateButtonEnum))
        for rating in SELECTION_ORDER:
            buttonModel = model.getRatingButtonsType()()
            buttonModel.setButtonVariant(_COMMON_TO_MODEL_ENUM_MAP[rating])
            buttonArray.addViewModel(buttonModel)

        buttonArray.invalidate()
