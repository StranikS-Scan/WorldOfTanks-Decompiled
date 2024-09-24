# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/page.py
from aih_constants import CTRL_MODE_NAME
from constants import ARENA_PERIOD
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.daapi.view.battle.shared import SharedPage, finish_sound_player, drone_music_player
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.Scaleform.daapi.view.battle.shared.tabbed_full_stats import TabsAliases
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from shared_utils import CONST_CONTAINER

class DynamicAliases(CONST_CONTAINER):
    PREBATTLE_TIMER_SOUND_PLAYER = 'prebattleTimerSoundPlayer'
    FINISH_SOUND_PLAYER = 'finishSoundPlayer'
    DRONE_MUSIC_PLAYER = 'droneMusicPlayer'


class ClassicComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(ClassicComponentsConfig, self).__init__(((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
           BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
           DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
           BATTLE_VIEW_ALIASES.PLAYERS_PANEL,
           BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
           BATTLE_VIEW_ALIASES.HINT_PANEL,
           BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL,
           DynamicAliases.DRONE_MUSIC_PLAYER)),
         (BATTLE_CTRL_ID.PERKS, (BATTLE_VIEW_ALIASES.SITUATION_INDICATORS,)),
         (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, DynamicAliases.DRONE_MUSIC_PLAYER)),
         (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
         (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
         (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.DRONE_MUSIC_PLAYER, BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, BATTLE_VIEW_ALIASES.PLAYERS_PANEL)),
         (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
         (BATTLE_CTRL_ID.SPECTATOR, (BATTLE_VIEW_ALIASES.SPECTATOR_VIEW,)),
         (BATTLE_CTRL_ID.PREBATTLE_SETUPS_CTRL, (BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, BATTLE_VIEW_ALIASES.DAMAGE_PANEL)),
         (BATTLE_CTRL_ID.AMMO, (BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL))), viewsConfig=((DynamicAliases.DRONE_MUSIC_PLAYER, drone_music_player.DroneMusicPlayer), (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer)))


BATTLE_HINTS_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT, BATTLE_VIEW_ALIASES.NEWBIE_HINT)),), viewsConfig=())
COMMON_CLASSIC_CONFIG = ClassicComponentsConfig() + BATTLE_HINTS_CONFIG
EXTENDED_CLASSIC_CONFIG = COMMON_CLASSIC_CONFIG + ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (DynamicAliases.FINISH_SOUND_PLAYER,)), (BATTLE_CTRL_ID.TEAM_BASES, (DynamicAliases.FINISH_SOUND_PLAYER,)), (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.FINISH_SOUND_PLAYER,))), viewsConfig=((DynamicAliases.FINISH_SOUND_PLAYER, finish_sound_player.FinishSoundPlayer),))

class ClassicPage(SharedPage):

    def __init__(self, components=None, external=None, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        self._fullStatsAlias = fullStatsAlias
        if components is None:
            components = COMMON_CLASSIC_CONFIG if self.sessionProvider.isReplayPlaying else EXTENDED_CLASSIC_CONFIG
        super(ClassicPage, self).__init__(components=components, external=external)
        return

    def __del__(self):
        LOG_DEBUG('ClassicPage is deleted')

    def _toggleRadialMenu(self, isShown, allowAction=True):
        radialMenuLinkage = BATTLE_VIEW_ALIASES.RADIAL_MENU
        newbieHintLinkage = BATTLE_VIEW_ALIASES.NEWBIE_HINT
        radialMenu = self.getComponent(radialMenuLinkage)
        if radialMenu is None:
            return
        elif self._fullStatsAlias and self.as_isComponentVisibleS(self._fullStatsAlias):
            return
        else:
            if isShown:
                radialMenu.show()
                self.app.enterGuiControlMode(radialMenuLinkage, cursorVisible=False, enableAiming=False)
                if newbieHintLinkage in self.components:
                    self._setComponentsVisibility(hidden={newbieHintLinkage})
            else:
                self.app.leaveGuiControlMode(radialMenuLinkage)
                radialMenu.hide(allowAction)
                if newbieHintLinkage in self.components:
                    self._setComponentsVisibility(visible={newbieHintLinkage})
            return

    def _toggleFullStats(self, isShown, permanent=None, tabAlias=None):
        manager = self.app.containerManager
        if manager.isModalViewsIsExists() and isShown:
            return
        elif not self._fullStatsAlias:
            return
        else:
            fullStats = self.getComponent(self._fullStatsAlias)
            if fullStats is None:
                return
            doTabSwitch = fullStats.hasTabs and tabAlias is not None and fullStats.hasTab(tabAlias)
            if not doTabSwitch and tabAlias not in (None, TabsAliases.STATS):
                return
            ctrl = self.sessionProvider.shared.calloutCtrl
            if ctrl is not None and ctrl.isRadialMenuOpened():
                return
            if self.as_isComponentVisibleS(self._fullStatsAlias) != isShown:
                if isShown:
                    if not self._fsToggling:
                        self._fsToggling.update(self.as_getComponentsVisibilityS())
                    if permanent is not None:
                        self._fsToggling.difference_update(permanent)
                    if doTabSwitch:
                        fullStats.setActiveTab(tabAlias)
                    self._setComponentsVisibility(visible={self._fullStatsAlias}, hidden=self._fsToggling)
                    fullStats.onToggleVisibility(True)
                else:
                    self._setComponentsVisibility(visible=self._fsToggling, hidden={self._fullStatsAlias})
                    fullStats.onToggleVisibility(False)
                    if doTabSwitch:
                        fullStats.setActiveTab(None)
                    self._fsToggling.clear()
            if isShown:
                self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.FULL_STATS, cursorVisible=True, enableAiming=False)
            else:
                self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.FULL_STATS)
            return

    def _processHint(self, needShow):
        alias = BATTLE_VIEW_ALIASES.HINT_PANEL
        if needShow:
            if self._isBattleLoading:
                self._blToggling.add(alias)
            elif self._fsToggling:
                self._fsToggling.add(alias)
            elif self._isDestroyTimerShown:
                self._destroyTimerToggling.add(alias)
            elif not self.as_isComponentVisibleS(alias):
                self._setComponentsVisibility(visible={alias})
        elif self._isBattleLoading:
            self._blToggling.discard(alias)
        elif self._fsToggling:
            self._fsToggling.discard(alias)
        elif self._isDestroyTimerShown:
            self._destroyTimerToggling.discard(alias)
        elif self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(hidden={alias})

    def _processCallout(self, needShow):
        alias = BATTLE_VIEW_ALIASES.CALLOUT_PANEL
        if needShow:
            if self._isBattleLoading:
                self._blToggling.add(alias)
            elif self._fsToggling:
                self._fsToggling.add(alias)
            elif not self.as_isComponentVisibleS(alias):
                self._setComponentsVisibility(visible={alias})
        elif self._isBattleLoading:
            self._blToggling.discard(alias)
        elif self._fsToggling:
            self._fsToggling.discard(alias)
        elif self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(hidden={alias})

    def _handleRadialMenuCmd(self, event):
        self._toggleRadialMenu(isShown=event.ctx['isDown'])

    def _handleHelpEvent(self, event):
        ctrl = self.sessionProvider.shared.calloutCtrl
        if ctrl is not None and ctrl.isRadialMenuOpened():
            self._toggleRadialMenu(False, False)
            ctrl.resetRadialMenuData()
        return

    def _handleToggleFullStats(self, event):
        self._toggleFullStats(event.ctx['isDown'], tabAlias=TabsAliases.STATS)

    def _handleToggleFullStatsQuestProgress(self, event):
        self._toggleFullStats(event.ctx['isDown'], tabAlias=TabsAliases.QUESTS_PROGRESS)

    def _handleToggleFullStatsPersonalReserves(self, event):
        self._toggleFullStats(event.ctx['isDown'], tabAlias=TabsAliases.BOOSTERS)

    def _handleBattleNotifierVisibility(self):
        battleNotifierLinkage = BATTLE_VIEW_ALIASES.BATTLE_NOTIFIER
        if self.getComponent(battleNotifierLinkage):
            self._blToggling.add(battleNotifierLinkage)

    def _onBattleLoadingStart(self):
        self._toggleFullStats(isShown=False)
        super(ClassicPage, self)._onBattleLoadingStart()

    def _onBattleLoadingFinish(self):
        self._toggleFullStats(isShown=False)
        self._handleBattleNotifierVisibility()
        super(ClassicPage, self)._onBattleLoadingFinish()
        battleCtx = self.sessionProvider.getCtx()
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        if battleCtx.isPlayerObserver() and periodCtrl.getPeriod() in (ARENA_PERIOD.WAITING, ARENA_PERIOD.PREBATTLE):
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.DAMAGE_PANEL, BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL})

    def _handleGUIToggled(self, event):
        if not self._fullStatsAlias or not self.as_isComponentVisibleS(self._fullStatsAlias):
            self._toggleGuiVisible()

    def _onRespawnBaseMoving(self):
        super(ClassicPage, self)._onRespawnBaseMoving()
        if not self._canShowPostmortemTips:
            return
        if self._fullStatsAlias and self.as_isComponentVisibleS(self._fullStatsAlias):
            self._fsToggling.discard(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
            self._fsToggling.add(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL)
        else:
            self._reloadPostmortem()

    def _hasCalloutPanel(self):
        return True

    def _switchToPostmortem(self):
        super(ClassicPage, self)._switchToPostmortem()
        ctrl = self.sessionProvider.shared.calloutCtrl
        if ctrl is not None and ctrl.isRadialMenuOpened():
            self._toggleRadialMenu(False)
        if self._hasCalloutPanel() and self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.CALLOUT_PANEL):
            self._processCallout(needShow=False)
        self._toggleFullStats(isShown=False)
        if self._fullStatsAlias and self.as_isComponentVisibleS(self._fullStatsAlias):
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL})
            self._fsToggling.add(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
        return

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        super(ClassicPage, self)._onPostMortemSwitched(noRespawnPossible, respawnAvailable)
        if self.sessionProvider.getCtx().isPlayerObserver():
            self.as_onPostmortemActiveS(False)

    def _changeCtrlMode(self, ctrlMode):
        components = self._getComponentsVideoModeSwitching(ctrlMode)
        battleCtx = self.sessionProvider.getCtx()
        if battleCtx.isPlayerObserver():
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL})
        if ctrlMode == CTRL_MODE_NAME.VIDEO:
            self._setComponentsVisibility(hidden=components)
        else:
            self._setComponentsVisibility(visible=components)
        postmortemPanel = self.getComponent(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
        postmortemPanel.changeCtrlMode(ctrlMode)

    def _getComponentsVideoModeSwitching(self, ctrlMode):

        def invalidateSiegeVehicle(vehicleDescriptor):
            vehicleType = vehicleDescriptor.type
            return (vehicleType.hasSiegeMode or vehicleDescriptor.isTrackWithinTrack) and not vehicleType.isWheeledVehicle and not vehicleDescriptor.isDualgunVehicle

        if ctrlMode == CTRL_MODE_NAME.DEATH_FREE_CAM:
            components = {BATTLE_VIEW_ALIASES.SPECTATOR_VIEW}
        elif ctrlMode in (CTRL_MODE_NAME.KILL_CAM, CTRL_MODE_NAME.POSTMORTEM):
            components = {BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, BATTLE_VIEW_ALIASES.DAMAGE_PANEL, BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL}
        else:
            components = {BATTLE_VIEW_ALIASES.DAMAGE_PANEL, BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL, BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL}
        if ctrlMode not in CTRL_MODE_NAME.POSTMORTEM_CONTROL_MODES:
            ctrl = self.sessionProvider.shared.vehicleState
            vehicle = ctrl.getControllingVehicle()
            if vehicle is None:
                LOG_ERROR('classic/page.py _changeCtrlMode vehicle is None in replay!')
            if vehicle is not None and invalidateSiegeVehicle(vehicle.typeDescriptor):
                components.add(BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR)
            if vehicle and vehicle.typeDescriptor.hasRocketAcceleration:
                components.add(BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR)
        battleCtx = self.sessionProvider.getCtx()
        if battleCtx.isPlayerObserver():
            components.discard(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
        return components

    def __hideDamageLogPanel(self):
        damageLogPanel = self.getComponent(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL)
        return not damageLogPanel.isSwitchToVehicle()

    def _onKillCamSimulationStart(self):
        self._toggleFullStats(isShown=False)
        super(ClassicPage, self)._onKillCamSimulationStart()

    def _onKillCamSimulationFinish(self):
        self._toggleFullStats(isShown=False)
        super(ClassicPage, self)._onKillCamSimulationFinish()
