# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/page.py
from logging import getLogger
import BigWorld
from aih_constants import CTRL_MODE_NAME
from avatar_components.avatar_chat_key_handling import AvatarChatKeyHandling
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gameplay import PlayerEventID
from story_mode.gui.scaleform.daapi.view.battle.page_base import StoryModeBattlePageBase, STORY_MODE_EXTERNAL_COMPONENTS
from story_mode.gui.scaleform.genConsts.STORY_MODE_BATTLE_VIEW_ALIASES import STORY_MODE_BATTLE_VIEW_ALIASES
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode_common.story_mode_constants import LOGGER_NAME
_logger = getLogger(LOGGER_NAME)

class DynamicAliases(CONST_CONTAINER):
    PREBATTLE_TIMER_SOUND_PLAYER = 'prebattleTimerSoundPlayer'


ONBOARDING_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, STORY_MODE_BATTLE_VIEW_ALIASES.STORY_MODE_TIMER)),
 (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
 (BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.NEWBIE_HINT,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,))), viewsConfig=((DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer),))

class OnboardingBattlePage(StoryModeBattlePageBase, ClassicPage):
    storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __init__(self, components=ONBOARDING_CONFIG, external=STORY_MODE_EXTERNAL_COMPONENTS, fullStatsAlias=None):
        super(OnboardingBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        self._visibleComponents = set()

    def reload(self):
        self.gameplay.postStateEvent(PlayerEventID.AVATAR_SHOW_GUI)
        self.fireEvent(events.GameEvent(events.GameEvent.GUI_VISIBILITY, {'visible': True}), scope=EVENT_BUS_SCOPE.BATTLE)
        player = BigWorld.player()
        if isinstance(player, AvatarChatKeyHandling):
            player.setKeyHandling(False)
        super(OnboardingBattlePage, self).reload()

    def _populate(self):
        super(OnboardingBattlePage, self)._populate()
        player = BigWorld.player()
        if isinstance(player, AvatarChatKeyHandling):
            player.setKeyHandling(False)

    def _onBattleLoadingStart(self):
        if not self._visibleComponents:
            self._visibleComponents = set(self.as_getComponentsVisibilityS())
        self._visibleComponents.discard(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
        self._blToggling = set(self._visibleComponents)
        super(OnboardingBattlePage, self)._onBattleLoadingStart()

    def _onKillCamSimulationFinish(self):
        self._visibleComponents.discard(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)

    def _changeCtrlMode(self, ctrlMode):
        super(OnboardingBattlePage, self)._changeCtrlMode(ctrlMode)
        if ctrlMode is CTRL_MODE_NAME.POSTMORTEM:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL})

    def _setComponentsVisibility(self, visible=None, hidden=None):
        if visible is not None and BATTLE_VIEW_ALIASES.BATTLE_LOADING in visible:
            visible.remove(BATTLE_VIEW_ALIASES.BATTLE_LOADING)
        if hidden is not None and BATTLE_VIEW_ALIASES.BATTLE_LOADING in hidden:
            hidden.remove(BATTLE_VIEW_ALIASES.BATTLE_LOADING)
        super(OnboardingBattlePage, self)._setComponentsVisibility(visible, hidden)
        return
