# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/page.py
from __future__ import absolute_import
import typing
import BigWorld
import BattleReplay
from Avatar import PlayerAvatar
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
from gui.battle_control import avatar_getter, event_dispatcher
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, TabsAliases
from gui.impl.gen import R
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from halloween.gui.impl.battle.full_stats import FullEventStatsWindow
from halloween.gui.impl.battle.halloween_battle_loading import HalloweenBattleLoadingWindow
from halloween.gui.scaleform.daapi.view.battle.indicators import hwCreateDamageIndicator
from halloween.gui.scaleform.daapi.view.battle.markers2d.manager import HalloweenMarkersManager
from halloween.gui.scaleform.daapi.view.battle.players_panel import HWPlayersPanel
from halloween.gui.scaleform.daapi.view.battle.shared.crosshair import HalloweenCrosshairPanelContainer
from halloween.gui.scaleform.daapi.view.meta.HalloweenBattlePageMeta import HalloweenBattlePageMeta
from halloween.gui.scaleform.genConsts.HALLOWEEN_BATTLE_VIEW_ALIASES import HALLOWEEN_BATTLE_VIEW_ALIASES as HW_ALIASES
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.impl import IGuiLoader
from PlayerEvents import g_playerEvents
import CommandMapping
if typing.TYPE_CHECKING:
    from typing import Optional

class _ComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_ComponentsConfig, self).__init__(((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
           DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
           BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
           BATTLE_VIEW_ALIASES.HINT_PANEL,
           DynamicAliases.DRONE_MUSIC_PLAYER,
           HW_ALIASES.HW_PLAYERS_PANEL)),
         (BATTLE_CTRL_ID.PERKS, (BATTLE_VIEW_ALIASES.EVENT_BUFFS_PANEL,)),
         (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, DynamicAliases.DRONE_MUSIC_PLAYER)),
         (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
         (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
         (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.DRONE_MUSIC_PLAYER, HW_ALIASES.HW_PLAYERS_PANEL)),
         (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
         (BATTLE_CTRL_ID.PREBATTLE_SETUPS_CTRL, (BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, BATTLE_VIEW_ALIASES.DAMAGE_PANEL)),
         (BATTLE_CTRL_ID.AMMO, (BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL)),
         (BATTLE_CTRL_ID.HIT_DIRECTION, (BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR, BATTLE_VIEW_ALIASES.HIT_DIRECTION)),
         (BATTLE_CTRL_ID.BATTLE_HINTS, (HW_ALIASES.BUFF_NOTIFICATION_SYSTEM,
           BATTLE_VIEW_ALIASES.BATTLE_HINT,
           HW_ALIASES.PINNABLE_BATTLE_HINT,
           HW_ALIASES.PROGRESS_BAR_BATTLE_HINT,
           HW_ALIASES.PHASE_MODIFIER_HINT))), viewsConfig=((DynamicAliases.DRONE_MUSIC_PLAYER, drone_music_player.DroneMusicPlayer),
         (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer),
         (BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR, createPredictionIndicator),
         (BATTLE_VIEW_ALIASES.HIT_DIRECTION, hwCreateDamageIndicator),
         (HW_ALIASES.HW_PLAYERS_PANEL, HWPlayersPanel)))


_CONFIG = _ComponentsConfig()
_EXTENDED_CONFIG = _CONFIG + ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (DynamicAliases.FINISH_SOUND_PLAYER,)), (BATTLE_CTRL_ID.TEAM_BASES, (DynamicAliases.FINISH_SOUND_PLAYER,)), (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.FINISH_SOUND_PLAYER,))), viewsConfig=((DynamicAliases.FINISH_SOUND_PLAYER, finish_sound_player.FinishSoundPlayer),))
_EXTERNAL_COMPONENTS = (HalloweenCrosshairPanelContainer, HalloweenMarkersManager)
_POSTMORTEM_HIDE_VIEW = {BATTLE_VIEW_ALIASES.EVENT_BUFFS_PANEL,
 HW_ALIASES.POINT_COUNTER,
 BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,
 BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR,
 BATTLE_VIEW_ALIASES.UPGRADE_PANEL,
 HW_ALIASES.PHASE_MODIFIER_HINT}
_ANOMALY_RECIPES_PERMANENT_VIEW = {BATTLE_VIEW_ALIASES.UPGRADE_PANEL, BATTLE_VIEW_ALIASES.EVENT_TIMER}
_POSTMORTEM_HIDE_BTN_HINTS = (CommandMapping.CMD_SHOW_HELP,
 CommandMapping.CMD_COMMANDER_CAM,
 CommandMapping.CMD_QUEST_PROGRESS_SHOW,
 CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMAND,
 CommandMapping.CMD_SHOW_PERSONAL_RESERVES)
_ROUND_FINISHED_HIDE_VIEW = {BATTLE_VIEW_ALIASES.HINT_PANEL,
 HW_ALIASES.PINNABLE_BATTLE_HINT,
 HW_ALIASES.PROGRESS_BAR_BATTLE_HINT,
 BATTLE_VIEW_ALIASES.EVENT_TIMER,
 BATTLE_VIEW_ALIASES.UPGRADE_PANEL}

class HalloweenBattlePage(HalloweenBattlePageMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, components=None, external=_EXTERNAL_COMPONENTS, fullStatsAlias=None, **kwargs):
        if components is None:
            components = _CONFIG if self.sessionProvider.isReplayPlaying else _EXTENDED_CONFIG
        self._guiLoader = dependency.instance(IGuiLoader)
        self._currentFullScreenAlias = None
        self._hasHints = False
        self._isAutoGuiTogglingActive = False
        self._arenaPeriod = None
        super(HalloweenBattlePage, self).__init__(components=components, external=external, fullStatsAlias=None)
        return

    def isAnyFullScreenViewVisible(self, viewAlias=None):
        view = self._guiLoader.windowsManager.getViewByLayoutID(R.views.halloween.mono.battle.tab_screen())
        isTabScreensVisible = view is not None and not view.getParentWindow().isHidden()
        isScreenByAliasVisible = viewAlias and self.isFullScreenVisible(viewAlias)
        return isTabScreensVisible or isScreenByAliasVisible

    def isFullScreenVisible(self, viewAlias):
        return self._currentFullScreenAlias == viewAlias

    def setComponentsVisibilityWithFade(self, visible=None, hidden=None):
        if hidden:
            if self.isFullScreenVisible(TabsAliases.QUESTS_PROGRESS):
                hidden.difference_update(_ANOMALY_RECIPES_PERMANENT_VIEW)
            self._hasHints = True
        else:
            vehicle = BigWorld.player().vehicle
            if (vehicle and not vehicle.isPlayerVehicle or not self.hwBattleGuiCtrl.currentUpgradeOptions) and visible and BATTLE_VIEW_ALIASES.UPGRADE_PANEL in visible:
                visible.remove(BATTLE_VIEW_ALIASES.UPGRADE_PANEL)
            self._hasHints = False
        super(HalloweenBattlePage, self).setComponentsVisibilityWithFade(visible, hidden)

    @property
    def hwBattleGuiCtrl(self):
        return self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    def _populate(self):
        super(HalloweenBattlePage, self)._populate()
        LOG_DEBUG('-=>> Halloween battle page is created.')

    def _dispose(self):
        super(HalloweenBattlePage, self)._dispose()
        LOG_DEBUG('-=>> Halloween battle page is destroyed.')

    def _switchToPostmortem(self):
        super(HalloweenBattlePage, self)._switchToPostmortem()
        self._setComponentsVisibility(hidden=_POSTMORTEM_HIDE_VIEW)
        hintPanel = self.getComponent(BATTLE_VIEW_ALIASES.HINT_PANEL)
        if hintPanel:
            for hintBtnID in _POSTMORTEM_HIDE_BTN_HINTS:
                hintPanel.removeBtnHint(hintBtnID)

        if self.isAnyFullScreenViewVisible():
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL})
            self._fsToggling.add(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
            self._fsToggling.difference_update(_POSTMORTEM_HIDE_VIEW)

    def _reloadPostmortem(self):
        super(HalloweenBattlePage, self)._reloadPostmortem()
        if self.isAnyFullScreenViewVisible() or self._currentFullScreenAlias:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL})
            self._fsToggling.discard(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
            self._fsToggling.update(_POSTMORTEM_HIDE_VIEW)
            self._fsToggling.update({BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL})
        else:
            visible = _POSTMORTEM_HIDE_VIEW.copy()
            visible.remove(BATTLE_VIEW_ALIASES.UPGRADE_PANEL)
            self._setComponentsVisibility(visible=visible)
        if self.sessionProvider.isReplayPlaying:
            self.as_onPostmortemActiveS(self._isInPostmortem)

    def _getComponentsVideoModeSwitching(self, ctrlMode):
        components = super(HalloweenBattlePage, self)._getComponentsVideoModeSwitching(ctrlMode)
        if self.isAnyFullScreenViewVisible():
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR})
        return components

    def _handleGUIToggled(self, event):
        if not self.isAnyFullScreenViewVisible():
            self._toggleGuiVisible()

    def _handleHelpEvent(self, event):
        super(HalloweenBattlePage, self)._handleHelpEvent(event)
        if self.isFullScreenVisible(TabsAliases.QUESTS_PROGRESS):
            self._toggleFullStats(isShown=False, permanent=_ANOMALY_RECIPES_PERMANENT_VIEW, tabAlias=TabsAliases.QUESTS_PROGRESS)

    def _handleToggleFullStatsQuestProgress(self, event):
        isShown = event.ctx['isDown']
        self._toggleFullStats(isShown, permanent=_ANOMALY_RECIPES_PERMANENT_VIEW, tabAlias=TabsAliases.QUESTS_PROGRESS)

    def _toggleRadialMenu(self, isShown, allowAction=True):
        if self.isAnyFullScreenViewVisible(viewAlias=TabsAliases.QUESTS_PROGRESS):
            return
        super(HalloweenBattlePage, self)._toggleRadialMenu(isShown, allowAction)

    def _toggleFullStats(self, isShown, permanent=None, tabAlias=None):
        manager = self.app.containerManager
        if manager.isModalViewsIsExists():
            return
        else:
            ctrl = self.sessionProvider.shared.calloutCtrl
            if ctrl is not None and ctrl.isRadialMenuOpened():
                return
            hasVisibleScreen = self.isAnyFullScreenViewVisible(viewAlias=self._currentFullScreenAlias)
            if isShown == hasVisibleScreen:
                return
            if self._currentFullScreenAlias and self._currentFullScreenAlias != tabAlias:
                if self._currentFullScreenAlias != TabsAliases.QUESTS_PROGRESS:
                    return
            if isShown:
                if manager.getViewByKey(ViewKey(VIEW_ALIAS.INGAME_MENU)):
                    return
                if self._guiLoader.windowsManager.findWindows(lambda w: w.isModal()):
                    return False
                visible = set()
                if tabAlias == TabsAliases.QUESTS_PROGRESS:
                    if self._arenaPeriod == ARENA_PERIOD.AFTERBATTLE:
                        return
                    if not self.isGuiVisible():
                        self._isAutoGuiTogglingActive = True
                        self._toggleGuiVisible()
                    event_dispatcher.toggleCrosshairVisibility()
                    visible.add(HW_ALIASES.ANOMALY_RECIPES_VIEW)
                    if (self._hasHints or self._isInPostmortem) and self.hwBattleGuiCtrl.currentUpgradeOptions:
                        visible.add(BATTLE_VIEW_ALIASES.UPGRADE_PANEL)
                    self.hwBattleGuiCtrl.updateAnomalyViewVisibility(isShown)
                else:
                    self.__showBattlePageGFComponent(R.views.halloween.mono.battle.tab_screen(), FullEventStatsWindow)
                if not self._fsToggling:
                    self._fsToggling.update(self.as_getComponentsVisibilityS())
                if permanent is not None:
                    self._fsToggling.difference_update(permanent)
                self._setComponentsVisibility(visible=visible, hidden=self._fsToggling)
            else:
                self.__destroyBattlePageGFComponent(R.views.halloween.mono.battle.tab_screen())
                hidden = set()
                if self.isFullScreenVisible(TabsAliases.QUESTS_PROGRESS):
                    if self._isAutoGuiTogglingActive:
                        self._toggleGuiVisible()
                        self._isAutoGuiTogglingActive = False
                    else:
                        event_dispatcher.toggleCrosshairVisibility()
                    if self._hasHints or not self.hwBattleGuiCtrl.currentUpgradeOptions or self._isInPostmortem:
                        hidden.add(BATTLE_VIEW_ALIASES.UPGRADE_PANEL)
                    if self._isInPostmortem:
                        vehicleAttached = BigWorld.player().getVehicleAttached()
                        if vehicleAttached is not None and vehicleAttached.isPlayerVehicle:
                            self._fsToggling.add(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL)
                    hidden.add(HW_ALIASES.ANOMALY_RECIPES_VIEW)
                    self.hwBattleGuiCtrl.updateAnomalyViewVisibility(isShown)
                self._setComponentsVisibility(visible=self._fsToggling, hidden=hidden)
                self._fsToggling.clear()
            if self._isInPostmortem:
                self.as_onPostmortemActiveS(not isShown)
            if isShown:
                self.app.enterGuiControlMode(R.views.halloween.mono.battle.tab_screen(), cursorVisible=True, enableAiming=False)
            else:
                self.app.leaveGuiControlMode(R.views.halloween.mono.battle.tab_screen())
            self._currentFullScreenAlias = tabAlias if isShown else None
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
        visible.add(BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR)
        self.__showBattlePageGFComponent(R.views.halloween.mono.battle.battle_loading(), HalloweenBattleLoadingWindow)
        self.app.enterGuiControlMode(R.views.halloween.mono.battle.battle_loading(), cursorVisible=True, enableAiming=False)
        self._blToggling.difference_update(additionalToggling)
        self._setComponentsVisibility(visible=visible, hidden=self._blToggling)
        self._blToggling.update(additionalToggling)
        self._blToggling.discard(HW_ALIASES.ANOMALY_RECIPES_VIEW)
        return

    def _onBattleLoadingFinish(self):
        self._toggleFullStats(isShown=False)
        self._handleBattleNotifierVisibility()
        self._isBattleLoading = False
        battleLoadingLayoutID = R.views.halloween.mono.battle.battle_loading()
        self.app.leaveGuiControlMode(battleLoadingLayoutID)
        if self.sessionProvider.isReplayPlaying:
            self.__hideBattlePageGFComponent(battleLoadingLayoutID)
        else:
            self.__destroyBattlePageGFComponent(battleLoadingLayoutID)
        self._setComponentsVisibility(visible=self._blToggling)
        self._blToggling.clear()
        for component in self._external:
            component.active(True)

        self.sessionProvider.shared.hitDirection.setVisible(True)
        battleCtx = self.sessionProvider.getCtx()
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        if battleCtx.isPlayerObserver() and periodCtrl.getPeriod() in (ARENA_PERIOD.WAITING, ARENA_PERIOD.PREBATTLE):
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.DAMAGE_PANEL, BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL})
        if BigWorld.player().arena.period != ARENA_PERIOD.BATTLE:
            self._setComponentsVisibility(hidden={HW_ALIASES.HW_PLAYERS_PANEL, HW_ALIASES.PHASE_INDICATOR})

    def _startBattleSession(self):
        super(HalloweenBattlePage, self)._startBattleSession()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPlayerFeedbackReceived += self.__onPlayerFeedbackReceived
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onSelectAnomaly += self.__onSelectAnomaly
            hwBattleGuiCtrl.onUpgradeOptionsUpdated += self.__onUpgradeOptionsUpdated
            hwBattleGuiCtrl.onChangeAnomaliesViewVisibility += self.__onChangeAnomaliesViewVisibility
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        avatar = BigWorld.player()
        if avatar is not None:
            avatar.onAvatarVehicleChanged += self.__onAvatarVehicleChanged
        return

    def _stopBattleSession(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPlayerFeedbackReceived -= self.__onPlayerFeedbackReceived
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onSelectAnomaly -= self.__onSelectAnomaly
            hwBattleGuiCtrl.onUpgradeOptionsUpdated -= self.__onUpgradeOptionsUpdated
            hwBattleGuiCtrl.onChangeAnomaliesViewVisibility -= self.__onChangeAnomaliesViewVisibility
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        player = BigWorld.player()
        if isinstance(player, PlayerAvatar):
            player.onAvatarVehicleChanged -= self.__onAvatarVehicleChanged
        super(HalloweenBattlePage, self)._stopBattleSession()
        return

    def _canShowPostmortemTips(self):
        return super(HalloweenBattlePage, self)._canShowPostmortemTips() or BattleReplay.g_replayCtrl.isPlaying

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self._setComponentsVisibility(visible={HW_ALIASES.HW_PLAYERS_PANEL, HW_ALIASES.PHASE_INDICATOR})
        elif period == ARENA_PERIOD.AFTERBATTLE and self.hwBattleGuiCtrl.isAnomaliesViewVisible:
            self._toggleFullStats(False, tabAlias=TabsAliases.QUESTS_PROGRESS)
        self._arenaPeriod = period

    def __showBattlePageGFComponent(self, layoutID, windowClass):
        view = self._guiLoader.windowsManager.getViewByLayoutID(layoutID)
        if view is not None:
            view.getParentWindow().show()
        else:
            window = windowClass()
            window.load()
        return

    def __destroyBattlePageGFComponent(self, layoutID):
        view = self._guiLoader.windowsManager.getViewByLayoutID(layoutID)
        if view is not None:
            view.destroyWindow()
        return

    def __hideBattlePageGFComponent(self, layoutID):
        view = self._guiLoader.windowsManager.getViewByLayoutID(layoutID)
        if view is not None:
            view.getParentWindow().hide()
        return

    def __onPlayerFeedbackReceived(self, feedback):
        for event in feedback:
            eventType = event.getType()
            if eventType == FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER:
                damageExtra = event.getExtra()
                if damageExtra.isDeathZone():
                    self.as_updateDamageScreenS(True)

    def __onSelectAnomaly(self, _):
        if self.isFullScreenVisible(TabsAliases.QUESTS_PROGRESS):
            self._toggleFullStats(False, tabAlias=TabsAliases.QUESTS_PROGRESS)

    def __onUpgradeOptionsUpdated(self, newUpgrades):
        if self.isFullScreenVisible(TabsAliases.QUESTS_PROGRESS):
            hidden, visible = set(), set()
            if newUpgrades:
                visible.add(BATTLE_VIEW_ALIASES.UPGRADE_PANEL)
            else:
                hidden.add(BATTLE_VIEW_ALIASES.UPGRADE_PANEL)
            self._setComponentsVisibility(visible=visible, hidden=hidden)

    def __onChangeAnomaliesViewVisibility(self, isVisible):
        hidden, visible = set(), set()
        if isVisible and self.hwBattleGuiCtrl.currentUpgradeOptions:
            visible.add(BATTLE_VIEW_ALIASES.UPGRADE_PANEL)
        elif self._hasHints:
            hidden.add(BATTLE_VIEW_ALIASES.UPGRADE_PANEL)
        self._setComponentsVisibility(visible=visible, hidden=hidden)

    def __onRoundFinished(self, winningTeam, reason):
        self._setComponentsVisibility(hidden=_ROUND_FINISHED_HIDE_VIEW)

    def __onAvatarVehicleChanged(self):
        if self._isInPostmortem:
            vehicleAttached = BigWorld.player().getVehicleAttached()
            if vehicleAttached is not None and vehicleAttached.isPlayerVehicle and not self.isAnyFullScreenViewVisible(viewAlias=TabsAliases.QUESTS_PROGRESS):
                self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL})
            else:
                self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL})
        return
