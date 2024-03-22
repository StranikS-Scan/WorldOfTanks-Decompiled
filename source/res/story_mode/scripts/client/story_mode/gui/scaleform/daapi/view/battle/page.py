# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/page.py
from logging import getLogger
import BattleReplay
import BigWorld
from PlayerEvents import g_playerEvents
from aih_constants import CTRL_MODE_NAME
from avatar_components.avatar_chat_key_handling import AvatarChatKeyHandling
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.event_dispatcher import toggleCrosshairVisibility
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gameplay import PlayerEventID
from story_mode.gui.impl.battle.prebattle_window import getOpenedPrebattleView
from story_mode.gui.scaleform.daapi.view.battle.markers2d import StoryModeMarkersManager
from story_mode.gui.scaleform.genConsts.STORY_MODE_BATTLE_VIEW_ALIASES import STORY_MODE_BATTLE_VIEW_ALIASES
from story_mode.gui.shared.event_dispatcher import showIntroVideo, showPrebattleWindow
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode_common.story_mode_constants import LOGGER_NAME, FIRST_MISSION_ID
_logger = getLogger(LOGGER_NAME)

class DynamicAliases(CONST_CONTAINER):
    PREBATTLE_TIMER_SOUND_PLAYER = 'prebattleTimerSoundPlayer'


STORY_MODE_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, STORY_MODE_BATTLE_VIEW_ALIASES.STORY_MODE_TIMER)),
 (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
 (BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.NEWBIE_HINT,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,))), viewsConfig=((DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer),))
_STORY_MODE_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, StoryModeMarkersManager)

class StoryModeBattlePage(ClassicPage):
    storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __init__(self, components=STORY_MODE_CONFIG, external=_STORY_MODE_EXTERNAL_COMPONENTS, fullStatsAlias=None):
        super(StoryModeBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        self._isWinMessageShown = False
        self._visibleComponents = set()

    @property
    def isWinMessageShown(self):
        return self._isWinMessageShown

    def reload(self):
        self._isWinMessageShown = False
        self.gameplay.postStateEvent(PlayerEventID.AVATAR_SHOW_GUI)
        self.fireEvent(events.GameEvent(events.GameEvent.GUI_VISIBILITY, {'visible': True}), scope=EVENT_BUS_SCOPE.BATTLE)
        player = BigWorld.player()
        if isinstance(player, AvatarChatKeyHandling):
            player.setKeyHandling(False)
        _logger.debug('-=>> Story mode battle page is reloaded.')
        super(StoryModeBattlePage, self).reload()

    def hideAll(self):
        self._setComponentsVisibility(hidden=self._visibleComponents)

    def showWinMessage(self, team, reason):
        gameMessagesPanel = self.getComponent(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL)
        gameMessagesPanel.sendEndGameMessage(team, reason)
        inputHandler = BigWorld.player().inputHandler
        if inputHandler.ctrlModeName != CTRL_MODE_NAME.ARCADE:
            inputHandler.onControlModeChanged(CTRL_MODE_NAME.ARCADE, preferredPos=inputHandler.getDesiredShotPoint())
        self.__onRoundFinished()
        self._isWinMessageShown = True

    def _populate(self):
        super(StoryModeBattlePage, self)._populate()
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        player = BigWorld.player()
        if isinstance(player, AvatarChatKeyHandling):
            player.setKeyHandling(False)
        _logger.debug('-=>> Story mode battle page is created.')

    def _dispose(self):
        super(StoryModeBattlePage, self)._dispose()
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        _logger.debug('-=>> Story mode battle page is destroyed.')

    def _hasBattleMessenger(self):
        return False

    def _hasCalloutPanel(self):
        return False

    def _onBattleLoadingStart(self):
        if not self._visibleComponents:
            self._visibleComponents = set(self.as_getComponentsVisibilityS())
        self._blToggling = set(self._visibleComponents)
        super(StoryModeBattlePage, self)._onBattleLoadingStart()
        missionId = self.sessionProvider.arenaVisitor.extra.getValue('missionId')
        _logger.debug('_onBattleLoadingStart: missionId=%s', missionId)
        prebattleWindow = getOpenedPrebattleView()
        if prebattleWindow is not None:
            prebattleWindow.restart()
        elif missionId is None or missionId == FIRST_MISSION_ID:
            showIntroVideo()
        else:
            showPrebattleWindow(missionId=missionId)
        return

    def _onKillCamSimulationFinish(self):
        self._visibleComponents.discard(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)

    def _changeCtrlMode(self, ctrlMode):
        super(StoryModeBattlePage, self)._changeCtrlMode(ctrlMode)
        if ctrlMode is CTRL_MODE_NAME.POSTMORTEM:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL})

    def _setComponentsVisibility(self, visible=None, hidden=None):
        if visible is not None and BATTLE_VIEW_ALIASES.BATTLE_LOADING in visible:
            visible.remove(BATTLE_VIEW_ALIASES.BATTLE_LOADING)
        if hidden is not None and BATTLE_VIEW_ALIASES.BATTLE_LOADING in hidden:
            hidden.remove(BATTLE_VIEW_ALIASES.BATTLE_LOADING)
        super(StoryModeBattlePage, self)._setComponentsVisibility(visible, hidden)
        return

    def _handleGUIToggled(self, event):
        if not self.sessionProvider.arenaVisitor.extra.getValue('isForceOnboarding') or BattleReplay.isPlaying():
            super(StoryModeBattlePage, self)._handleGUIToggled(event)
            if self._isVisible and self._isWinMessageShown:
                toggleCrosshairVisibility()

    def __onRoundFinished(self, *_):
        hideSet = set(self.as_getComponentsVisibilityS())
        hideSet.difference_update([BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, STORY_MODE_BATTLE_VIEW_ALIASES.SUBTITLES])
        self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, STORY_MODE_BATTLE_VIEW_ALIASES.SUBTITLES}, hidden=hideSet)
        if not self._isWinMessageShown:
            toggleCrosshairVisibility()
        avatar_getter.setComponentsVisibility(False)
