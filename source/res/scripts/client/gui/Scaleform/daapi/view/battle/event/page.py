# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/page.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from gui.Scaleform.daapi.view.battle.event import markers2d
from gui.Scaleform.daapi.view.battle.shared import period_music_listener, drone_music_player, finish_sound_player, SharedPage
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.framework import ViewTypes
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.game_control.race_sound_controller import RaceSoundController

class _FestivalRaceComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_FestivalRaceComponentsConfig, self).__init__(((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
           BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
           BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
           DynamicAliases.DRONE_MUSIC_PLAYER,
           DynamicAliases.PERIOD_MUSIC_LISTENER)),
         (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, DynamicAliases.DRONE_MUSIC_PLAYER)),
         (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,))), ((DynamicAliases.PERIOD_MUSIC_LISTENER, period_music_listener.PeriodMusicListener), (DynamicAliases.DRONE_MUSIC_PLAYER, drone_music_player.DroneMusicPlayer)))


COMMON_FESTIVAL_RACE_CONFIG = _FestivalRaceComponentsConfig()
EXTENDED_FESTIVAL_RACE_CONFIG = COMMON_FESTIVAL_RACE_CONFIG + ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (DynamicAliases.FINISH_SOUND_PLAYER,)), (BATTLE_CTRL_ID.TEAM_BASES, (DynamicAliases.FINISH_SOUND_PLAYER,)), (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.FINISH_SOUND_PLAYER,))), viewsConfig=((DynamicAliases.FINISH_SOUND_PLAYER, finish_sound_player.FinishSoundPlayer),))

class FestivalRaceBattlePage(SharedPage):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, components=None, external=None, fullStatsAlias=BATTLE_VIEW_ALIASES.FESTIVAL_RACE_FULL_STATS):
        self._ingameHelpToggling = set()
        self._fullStatsAlias = fullStatsAlias
        self._ingameHelpIsShown = False
        if components is None:
            components = COMMON_FESTIVAL_RACE_CONFIG if self.sessionProvider.isReplayPlaying else EXTENDED_FESTIVAL_RACE_CONFIG
        if external is None:
            external = (CrosshairPanelContainer, markers2d.EventRaceMarkersManager)
        super(FestivalRaceBattlePage, self).__init__(components=components, external=external)
        return

    def isHelpShown(self):
        return self._ingameHelpIsShown

    def hideIngameHelp(self, _):
        self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.FESTIVAL_RACE_INGAME_HELP}, visible=self._ingameHelpToggling)
        self._ingameHelpIsShown = False

    def _populate(self):
        super(FestivalRaceBattlePage, self)._populate()
        LOG_DEBUG('FestivalRaceBattlePage  is created.')
        self.addListener(events.GameEvent.EVENT_HELP_SHOW, self._showIngameHelp, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.EVENT_HELP_HIDE, self.hideIngameHelp, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__soundController = RaceSoundController()
        self.__soundController.init()

    def _dispose(self):
        super(FestivalRaceBattlePage, self)._dispose()
        if self.__soundController is not None:
            self.__soundController.destroy()
            self.__soundController = None
        LOG_DEBUG('Event battle page is destroyed.')
        return

    def _toggleRadialMenu(self, isShown):
        manager = self.app.containerManager
        if not manager.isContainerShown(ViewTypes.DEFAULT):
            return
        elif manager.isModalViewsIsExists():
            return
        else:
            radialMenu = self.getComponent(BATTLE_VIEW_ALIASES.RADIAL_MENU)
            if radialMenu is None:
                return
            elif self._fullStatsAlias and self.as_isComponentVisibleS(self._fullStatsAlias):
                return
            if isShown:
                radialMenu.show()
                self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.RADIAL_MENU, cursorVisible=False, enableAiming=False)
            else:
                self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.RADIAL_MENU)
                radialMenu.hide()
            return

    def _handleRadialMenuCmd(self, event):
        isDown = event.ctx['isDown']
        self._toggleRadialMenu(isDown)

    def _handleGUIToggled(self, event):
        self._toggleGuiVisible()

    def _handleToggleFullStats(self, event):
        isDown = event.ctx['isDown']
        self._toggleFullStats(isDown)

    def _handleToggleFullStatsQuestProgress(self, event):
        pass

    def _showIngameHelp(self, event):
        ingameHelp = self.getComponent(BATTLE_VIEW_ALIASES.FESTIVAL_RACE_INGAME_HELP)
        if ingameHelp is None:
            return
        elif self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.RADIAL_MENU):
            return
        else:
            manager = self.app.containerManager
            if manager.isModalViewsIsExists():
                return
            if event.ctx['source'] != '':
                ingameHelp.setHintEnabled(True)
            else:
                ingameHelp.setHintEnabled(False)
            if not self._ingameHelpToggling:
                self._ingameHelpToggling.update(self.as_getComponentsVisibilityS())
            self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.FESTIVAL_RACE_INGAME_HELP}, hidden=self._ingameHelpToggling)
            self._ingameHelpIsShown = True
            return

    def _toggleFullStats(self, isShown, permanent=None, tabIndex=None):
        manager = self.app.containerManager
        if manager.isModalViewsIsExists():
            return
        else:
            fullStats = self.getComponent(BATTLE_VIEW_ALIASES.FESTIVAL_RACE_FULL_STATS)
            if fullStats is None:
                return
            if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.RADIAL_MENU):
                return
            if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.FESTIVAL_RACE_FULL_STATS) != isShown:
                if isShown:
                    self._fsToggling.update(self.as_getComponentsVisibilityS())
                    self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.FESTIVAL_RACE_FULL_STATS}, hidden=self._fsToggling)
                else:
                    self._setComponentsVisibility(visible=self._fsToggling, hidden={BATTLE_VIEW_ALIASES.FESTIVAL_RACE_FULL_STATS})
                    self._fsToggling.clear()
                if self._isInPostmortem:
                    self.as_setPostmortemTipsVisibleS(not isShown)
                    if self.__hideDamageLogPanel():
                        self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL})
            return

    def __hideDamageLogPanel(self):
        damageLogPanel = self.getComponent(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL)
        return damageLogPanel.isSwitchToVehicle()
