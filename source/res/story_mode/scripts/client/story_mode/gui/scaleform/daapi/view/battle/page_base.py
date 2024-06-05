# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/page_base.py
from logging import getLogger
import BattleReplay
import BigWorld
from PlayerEvents import g_playerEvents
from aih_constants import CTRL_MODE_NAME
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control import avatar_getter
from gui.battle_control.event_dispatcher import toggleCrosshairVisibility
from story_mode.gui.impl.battle.prebattle_window import getOpenedPrebattleView
from story_mode.gui.scaleform.daapi.view.battle.markers2d import StoryModeMarkersManager
from story_mode.gui.scaleform.genConsts.STORY_MODE_BATTLE_VIEW_ALIASES import STORY_MODE_BATTLE_VIEW_ALIASES
from story_mode.gui.shared.event_dispatcher import showIntro
from story_mode_common.story_mode_constants import LOGGER_NAME
STORY_MODE_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, StoryModeMarkersManager)
_logger = getLogger(LOGGER_NAME)

class StoryModeBattlePageBase(object):

    def __init__(self, *args, **kwargs):
        super(StoryModeBattlePageBase, self).__init__(*args, **kwargs)
        self._isWinMessageShown = False

    @property
    def isWinMessageShown(self):
        return self._isWinMessageShown

    def hideAndStop(self):
        self._setComponentsVisibility(hidden=self.as_getComponentsVisibilityS())
        self._stopBattleSession()

    def reload(self):
        wasWinMessageShown = self._isWinMessageShown
        self._isWinMessageShown = False
        super(StoryModeBattlePageBase, self).reload()
        if wasWinMessageShown:
            toggleCrosshairVisibility()
        _logger.debug('[%s] reload', self)

    def _populate(self):
        super(StoryModeBattlePageBase, self)._populate()
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        _logger.debug('[%s] _populate', self)

    def _dispose(self):
        super(StoryModeBattlePageBase, self)._dispose()
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        _logger.debug('[%s] _dispose', self)

    def _handleGUIToggled(self, event):
        if not self.sessionProvider.arenaVisitor.extra.getValue('isForceOnboarding') or BattleReplay.isPlaying():
            super(StoryModeBattlePageBase, self)._handleGUIToggled(event)
            if self._isVisible and self._isWinMessageShown:
                toggleCrosshairVisibility()

    def _hasBattleMessenger(self):
        return False

    def _hasCalloutPanel(self):
        return False

    def showWinMessage(self, team, reason):
        gameMessagesPanel = self.getComponent(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL)
        gameMessagesPanel.sendEndGameMessage(team, reason)
        inputHandler = BigWorld.player().inputHandler
        if inputHandler.ctrlModeName != CTRL_MODE_NAME.ARCADE:
            inputHandler.onControlModeChanged(CTRL_MODE_NAME.ARCADE, preferredPos=inputHandler.getDesiredShotPoint())
        self.__onRoundFinished()

    def _onBattleLoadingStart(self):
        super(StoryModeBattlePageBase, self)._onBattleLoadingStart()
        missionId = self.sessionProvider.arenaVisitor.extra.getValue('missionId')
        _logger.debug('[%s] _onBattleLoadingStart: missionId=%s', self, missionId)
        prebattleWindow = getOpenedPrebattleView()
        if prebattleWindow is not None:
            prebattleWindow.restart()
        else:
            showIntro(missionId)
        return

    def __onRoundFinished(self, *_):
        hideSet = set(self.as_getComponentsVisibilityS())
        hideSet.difference_update([BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, STORY_MODE_BATTLE_VIEW_ALIASES.SUBTITLES])
        self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, STORY_MODE_BATTLE_VIEW_ALIASES.SUBTITLES}, hidden=hideSet)
        if not self._isWinMessageShown:
            toggleCrosshairVisibility()
            self._isWinMessageShown = True
        avatar_getter.setComponentsVisibility(False)
