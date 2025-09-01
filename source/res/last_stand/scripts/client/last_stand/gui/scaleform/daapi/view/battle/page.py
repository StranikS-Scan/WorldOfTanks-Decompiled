# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/page.py
import BigWorld
import BattleReplay
from debug_utils import LOG_DEBUG
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from gui.Scaleform.daapi.view.battle.shared import drone_music_player, finish_sound_player
from gui.Scaleform.daapi.view.battle.shared.indicators import createPredictionIndicator
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, FEEDBACK_EVENT_ID
from gui.impl.gen import R
from last_stand.gui.impl.battle.full_stats import FullEventStatsWindow, FullEventStatsView
from last_stand.gui.impl.battle.battle_loading_view import BattleLoadingWindow
from last_stand.gui.scaleform.daapi.view.battle.indicators import lsCreateDamageIndicator
from last_stand.gui.scaleform.daapi.view.battle.markers2d.manager import LSMarkersManager
from last_stand.gui.scaleform.daapi.view.battle.players_panel import LSPlayersPanel
from last_stand.gui.scaleform.daapi.view.battle.shared.crosshair import LSCrosshairPanelContainer
from last_stand.gui.scaleform.daapi.view.meta.LastStandBattlePageMeta import LastStandBattlePageMeta
from last_stand.gui.scaleform.genConsts.LS_BATTLE_VIEW_ALIASES import LS_BATTLE_VIEW_ALIASES as LS_ALIASES
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from PlayerEvents import g_playerEvents
import CommandMapping

class _ComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_ComponentsConfig, self).__init__(((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
           DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
           BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
           BATTLE_VIEW_ALIASES.HINT_PANEL,
           DynamicAliases.DRONE_MUSIC_PLAYER,
           LS_ALIASES.LS_PLAYERS_PANEL)),
         (BATTLE_CTRL_ID.PERKS, (BATTLE_VIEW_ALIASES.SITUATION_INDICATORS,)),
         (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, DynamicAliases.DRONE_MUSIC_PLAYER)),
         (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
         (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
         (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.DRONE_MUSIC_PLAYER, BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, LS_ALIASES.LS_PLAYERS_PANEL)),
         (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
         (BATTLE_CTRL_ID.AMMO, (BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,)),
         (BATTLE_CTRL_ID.HIT_DIRECTION, (BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR, BATTLE_VIEW_ALIASES.HIT_DIRECTION)),
         (BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT,
           LS_ALIASES.PINNABLE_BATTLE_HINT,
           LS_ALIASES.PROGRESS_BAR_BATTLE_HINT,
           LS_ALIASES.CONVOY_BATTLE_HINT))), viewsConfig=((DynamicAliases.DRONE_MUSIC_PLAYER, drone_music_player.DroneMusicPlayer),
         (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer),
         (BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR, createPredictionIndicator),
         (BATTLE_VIEW_ALIASES.HIT_DIRECTION, lsCreateDamageIndicator),
         (LS_ALIASES.LS_PLAYERS_PANEL, LSPlayersPanel)))


_CONFIG = _ComponentsConfig()
_EXTENDED_CONFIG = _CONFIG + ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (DynamicAliases.FINISH_SOUND_PLAYER,)), (BATTLE_CTRL_ID.TEAM_BASES, (DynamicAliases.FINISH_SOUND_PLAYER,)), (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.FINISH_SOUND_PLAYER,))), viewsConfig=((DynamicAliases.FINISH_SOUND_PLAYER, finish_sound_player.FinishSoundPlayer),))
_EXTERNAL_COMPONENTS = (LSCrosshairPanelContainer, LSMarkersManager)
_POSTMORTEM_HIDE_VIEW = {LS_ALIASES.POINT_COUNTER,
 BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL,
 BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,
 BATTLE_VIEW_ALIASES.SITUATION_INDICATORS}
_POSTMORTEM_HIDE_BTN_HINTS = (CommandMapping.CMD_SHOW_HELP,
 CommandMapping.CMD_COMMANDER_CAM,
 CommandMapping.CMD_QUEST_PROGRESS_SHOW,
 CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND,
 CommandMapping.CMD_SHOW_PERSONAL_RESERVES)
_BATTLE_LOADING_LAYOUT_ID = R.views.last_stand.mono.battle.battle_loading()

class LastStandBattlePage(LastStandBattlePageMeta):
    CONFIG = _CONFIG
    EXTENDED_CONFIG = _EXTENDED_CONFIG
    POSTMORTEM_HIDE_VIEW = _POSTMORTEM_HIDE_VIEW

    def __init__(self, components=None, external=_EXTERNAL_COMPONENTS, fullStatsAlias=None):
        if components is None:
            components = self.CONFIG if self.sessionProvider.isReplayPlaying else self.EXTENDED_CONFIG
        self.__guiLoader = dependency.instance(IGuiLoader)
        self.__fullStatsIsShown = False
        super(LastStandBattlePage, self).__init__(components=components, external=external, fullStatsAlias=None)
        return

    @property
    def hasTabScreen(self):
        view = self.__guiLoader.windowsManager.getViewByLayoutID(FullEventStatsView.getLayoutID())
        return view is not None and not view.getParentWindow().isHidden()

    def _populate(self):
        super(LastStandBattlePage, self)._populate()
        LOG_DEBUG('-=>> Last Stand battle page is created.')

    def _dispose(self):
        super(LastStandBattlePage, self)._dispose()
        LOG_DEBUG('-=>> Last Stand battle page is destroyed.')

    def _switchToPostmortem(self):
        super(LastStandBattlePage, self)._switchToPostmortem()
        self._setComponentsVisibility(hidden=self.POSTMORTEM_HIDE_VIEW)
        hintPanel = self.getComponent(BATTLE_VIEW_ALIASES.HINT_PANEL)
        if hintPanel:
            for hintBtnID in _POSTMORTEM_HIDE_BTN_HINTS:
                hintPanel.removeBtnHint(hintBtnID)

        if self.hasTabScreen:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL})
            self._fsToggling.add(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
            self._fsToggling.difference_update(self.POSTMORTEM_HIDE_VIEW)

    def _reloadPostmortem(self):
        super(LastStandBattlePage, self)._reloadPostmortem()
        if self.hasTabScreen:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL})
            self._fsToggling.discard(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
            self._fsToggling.update(self.POSTMORTEM_HIDE_VIEW)
        else:
            self._setComponentsVisibility(visible=self.POSTMORTEM_HIDE_VIEW)
        if self.sessionProvider.isReplayPlaying:
            self.as_onPostmortemActiveS(self._isInPostmortem)

    def _getComponentsVideoModeSwitching(self, ctrlMode):
        components = super(LastStandBattlePage, self)._getComponentsVideoModeSwitching(ctrlMode)
        if self.hasTabScreen:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR})
        return components

    def _handleGUIToggled(self, event):
        if not self.hasTabScreen:
            self._toggleGuiVisible()

    def _toggleRadialMenu(self, isShown, allowAction=True):
        if self.hasTabScreen:
            return
        super(LastStandBattlePage, self)._toggleRadialMenu(isShown, allowAction)

    def _toggleFullStats(self, isShown, permanent=None, tabAlias=None):
        manager = self.app.containerManager
        if manager.isModalViewsIsExists():
            return
        else:
            ctrl = self.sessionProvider.shared.calloutCtrl
            if ctrl is not None and ctrl.isRadialMenuOpened():
                return
            if self.hasTabScreen == self.__fullStatsIsShown == isShown:
                return
            if isShown:
                if manager.getViewByKey(ViewKey(VIEW_ALIAS.INGAME_MENU)):
                    return
                if self.__guiLoader.windowsManager.findWindows(lambda w: w.isModal()):
                    return
                self.__showBattlePageGFComponent(FullEventStatsView.getLayoutID(), FullEventStatsWindow)
                if not self._fsToggling:
                    self._fsToggling.update(self.as_getComponentsVisibilityS())
                if permanent is not None:
                    self._fsToggling.difference_update(permanent)
                self._setComponentsVisibility(hidden=self._fsToggling)
            else:
                self.__destroyBattlePageGFComponent(FullEventStatsView.getLayoutID())
                self._setComponentsVisibility(visible=self._fsToggling)
                self._fsToggling.clear()
            if self._isInPostmortem:
                self.as_onPostmortemActiveS(not isShown)
            if isShown:
                self.app.enterGuiControlMode(FullEventStatsView.getLayoutID(), cursorVisible=True, enableAiming=False)
            else:
                self.app.leaveGuiControlMode(FullEventStatsView.getLayoutID())
            self.__fullStatsIsShown = isShown
            return

    def _onBattleLoadingStart(self):
        self._toggleFullStats(isShown=False)
        self._isBattleLoading = True
        if not self._blToggling:
            self._blToggling = set(self.as_getComponentsVisibilityS())
        if not avatar_getter.isObserverSeesAll():
            self._blToggling.add(BATTLE_VIEW_ALIASES.BATTLE_MESSENGER)
        hintPanel = self.getComponent(BATTLE_VIEW_ALIASES.HINT_PANEL)
        if hintPanel and hintPanel.getActiveHint():
            self._blToggling.add(BATTLE_VIEW_ALIASES.HINT_PANEL)
        visible, additionalToggling = set(), set()
        if self.getComponent(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL) is not None:
            visible.add(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL)
            additionalToggling.add(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL)
        self.__showBattlePageGFComponent(_BATTLE_LOADING_LAYOUT_ID, BattleLoadingWindow)
        self.app.enterGuiControlMode(_BATTLE_LOADING_LAYOUT_ID, cursorVisible=True, enableAiming=False)
        self._blToggling.difference_update(additionalToggling)
        self._setComponentsVisibility(visible=visible, hidden=self._blToggling)
        self._blToggling.update(additionalToggling)
        return

    def _onBattleLoadingFinish(self):
        self._toggleFullStats(isShown=False)
        self._handleBattleNotifierVisibility()
        self._isBattleLoading = False
        self.app.leaveGuiControlMode(_BATTLE_LOADING_LAYOUT_ID)
        self.__destroyBattlePageGFComponent(_BATTLE_LOADING_LAYOUT_ID)
        self._setComponentsVisibility(visible=self._blToggling)
        self._blToggling.clear()
        for component in self._external:
            component.active(True)

        self.sessionProvider.shared.hitDirection.setVisible(True)
        battleCtx = self.sessionProvider.getCtx()
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        if battleCtx.isPlayerObserver() and periodCtrl.getPeriod() in (ARENA_PERIOD.WAITING, ARENA_PERIOD.PREBATTLE):
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.DAMAGE_PANEL, BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL})
        self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR})
        if BigWorld.player().arena.period != ARENA_PERIOD.BATTLE:
            self._setComponentsVisibility(hidden={LS_ALIASES.LS_PLAYERS_PANEL, LS_ALIASES.PHASE_INDICATOR})

    def _startBattleSession(self):
        super(LastStandBattlePage, self)._startBattleSession()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPlayerFeedbackReceived += self.__onPlayerFeedbackReceived
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        return

    def _stopBattleSession(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPlayerFeedbackReceived -= self.__onPlayerFeedbackReceived
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        super(LastStandBattlePage, self)._stopBattleSession()
        return

    def _canShowPostmortemTips(self):
        return super(LastStandBattlePage, self)._canShowPostmortemTips() or BattleReplay.g_replayCtrl.isPlaying

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self._setComponentsVisibility(visible={LS_ALIASES.LS_PLAYERS_PANEL, LS_ALIASES.PHASE_INDICATOR})
            if self.sessionProvider.isReplayPlaying:
                self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.EVENT_TIMER})

    def __showBattlePageGFComponent(self, layoutID, windowClass):
        view = self.__guiLoader.windowsManager.getViewByLayoutID(layoutID)
        if view is not None:
            view.getParentWindow().show()
        else:
            window = windowClass()
            window.load()
        return

    def __destroyBattlePageGFComponent(self, layoutID):
        view = self.__guiLoader.windowsManager.getViewByLayoutID(layoutID)
        if view is not None:
            view.destroyWindow()
        return

    def __onPlayerFeedbackReceived(self, feedback):
        for event in feedback:
            eventType = event.getType()
            if eventType == FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER:
                damageExtra = event.getExtra()
                if damageExtra.isDeathZone():
                    self.as_updateDamageScreenS(True)

    def __onRoundFinished(self, winningTeam, reason):
        aliases = {BATTLE_VIEW_ALIASES.HINT_PANEL,
         LS_ALIASES.PINNABLE_BATTLE_HINT,
         LS_ALIASES.CONVOY_BATTLE_HINT,
         LS_ALIASES.PROGRESS_BAR_BATTLE_HINT,
         BATTLE_VIEW_ALIASES.EVENT_TIMER}
        self._setComponentsVisibility(hidden=aliases)
