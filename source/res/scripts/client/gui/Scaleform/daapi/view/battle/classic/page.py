# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/page.py
from aih_constants import CTRL_MODE_NAME
from constants import ARENA_PERIOD
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.battle.shared import SharedPage, finish_sound_player, drone_music_player, period_music_listener
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from shared_utils import CONST_CONTAINER

class DynamicAliases(CONST_CONTAINER):
    PREBATTLE_TIMER_SOUND_PLAYER = 'prebattleTimerSoundPlayer'
    FINISH_SOUND_PLAYER = 'finishSoundPlayer'
    DRONE_MUSIC_PLAYER = 'droneMusicPlayer'
    PERIOD_MUSIC_LISTENER = 'periodMusicListener'


class _ClassicComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_ClassicComponentsConfig, self).__init__(((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
           BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
           DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
           BATTLE_VIEW_ALIASES.PLAYERS_PANEL,
           BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
           BATTLE_VIEW_ALIASES.HINT_PANEL,
           DynamicAliases.DRONE_MUSIC_PLAYER,
           DynamicAliases.PERIOD_MUSIC_LISTENER)),
         (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, DynamicAliases.DRONE_MUSIC_PLAYER)),
         (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
         (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
         (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,))), viewsConfig=((DynamicAliases.PERIOD_MUSIC_LISTENER, period_music_listener.PeriodMusicListener), (DynamicAliases.DRONE_MUSIC_PLAYER, drone_music_player.DroneMusicPlayer), (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer)))


COMMON_CLASSIC_CONFIG = _ClassicComponentsConfig()
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
        radialMenu = self.getComponent(radialMenuLinkage)
        if radialMenu is None:
            return
        elif self._fullStatsAlias and self.as_isComponentVisibleS(self._fullStatsAlias):
            return
        else:
            if isShown:
                radialMenu.show()
                self.app.enterGuiControlMode(radialMenuLinkage, cursorVisible=False, enableAiming=False)
            else:
                self.app.leaveGuiControlMode(radialMenuLinkage)
                radialMenu.hide(allowAction)
            return

    def _toggleFullStats(self, isShown, permanent=None, tabIndex=None):
        manager = self.app.containerManager
        if manager.isModalViewsIsExists():
            return
        elif not self._fullStatsAlias:
            return
        else:
            fullStats = self.getComponent(self._fullStatsAlias)
            if fullStats is None:
                return
            elif self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.RADIAL_MENU):
                return
            hasTabs = fullStats.hasTabs
            if not hasTabs and tabIndex > 0:
                return
            if self.as_isComponentVisibleS(self._fullStatsAlias) != isShown:
                if isShown:
                    if not self._fsToggling:
                        self._fsToggling.update(self.as_getComponentsVisibilityS())
                    if permanent is not None:
                        self._fsToggling.difference_update(permanent)
                    if hasTabs and tabIndex is not None:
                        fullStats.setActiveTabIndex(tabIndex)
                    self._setComponentsVisibility(visible={self._fullStatsAlias}, hidden=self._fsToggling)
                else:
                    self._setComponentsVisibility(visible=self._fsToggling, hidden={self._fullStatsAlias})
                    if hasTabs:
                        if tabIndex is not None:
                            fullStats.setActiveTabIndex(None)
                        fullStats.showQuestProgressAnimation()
                    self._fsToggling.clear()
                if self._isInPostmortem:
                    self.as_setPostmortemTipsVisibleS(not isShown)
                    if self.__hideDamageLogPanel():
                        self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL})
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
            elif not self.as_isComponentVisibleS(alias):
                self._setComponentsVisibility(visible={alias})
        elif self._isBattleLoading:
            self._blToggling.discard(alias)
        elif self._fsToggling:
            self._fsToggling.discard(alias)
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
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.RADIAL_MENU):
            self._toggleRadialMenu(False, False)

    def _handleToggleFullStats(self, event):
        self._toggleFullStats(event.ctx['isDown'], tabIndex=0)

    def _handleToggleFullStatsQuestProgress(self, event):
        self._toggleFullStats(event.ctx['isDown'], tabIndex=1)

    def _onBattleLoadingStart(self):
        self._toggleFullStats(isShown=False)
        super(ClassicPage, self)._onBattleLoadingStart()

    def _onBattleLoadingFinish(self):
        self._toggleFullStats(isShown=False)
        super(ClassicPage, self)._onBattleLoadingFinish()
        battleCtx = self.sessionProvider.getCtx()
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        if battleCtx.isPlayerObserver() and periodCtrl.getPeriod() in (ARENA_PERIOD.WAITING, ARENA_PERIOD.PREBATTLE):
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.DAMAGE_PANEL, BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL})

    def _handleGUIToggled(self, event):
        if self._fullStatsAlias and not self.as_isComponentVisibleS(self._fullStatsAlias):
            self._toggleGuiVisible()

    def _switchToPostmortem(self):
        super(ClassicPage, self)._switchToPostmortem()
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.RADIAL_MENU):
            self._toggleRadialMenu(False)
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.CALLOUT_PANEL):
            self._processCallout(needShow=False)

    def _changeCtrlMode(self, ctrlMode):

        def invalidateSiegeVehicle(vehicleType):
            return 'siegeMode' in vehicleType.tags and 'wheeledVehicle' not in vehicleType.tags and 'dualgun' not in vehicleType.tags

        components = {BATTLE_VIEW_ALIASES.DAMAGE_PANEL, BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL, BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL}
        if ctrlMode != CTRL_MODE_NAME.POSTMORTEM:
            ctrl = self.sessionProvider.shared.vehicleState
            vehicle = ctrl.getControllingVehicle()
            if invalidateSiegeVehicle(vehicle.typeDescriptor.type):
                components.add(BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR)
        if ctrlMode == CTRL_MODE_NAME.VIDEO:
            self._setComponentsVisibility(hidden=components)
        else:
            self._setComponentsVisibility(visible=components)

    def __hideDamageLogPanel(self):
        damageLogPanel = self.getComponent(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL)
        return damageLogPanel.isSwitchToVehicle()
