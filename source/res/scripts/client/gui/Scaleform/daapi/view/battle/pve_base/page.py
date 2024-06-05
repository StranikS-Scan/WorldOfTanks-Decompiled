# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/page.py
import typing
import BattleReplay
from aih_constants import CTRL_MODE_NAME
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.classic import ClassicPage
from gui.Scaleform.daapi.view.battle.classic.page import COMMON_CLASSIC_CONFIG, EXTENDED_CLASSIC_CONFIG, DynamicAliases
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.events import ViewEventType
from pve_battle_hud import WidgetType
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.minimap import MinimapClientModel
    from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.chat import ChatModel
    from gui.battle_control.controllers.vse_hud_settings_ctrl.settings.respawn_hud import RespawnHUDClientModel
    from gui.shared.events import LoadViewEvent
_REMOVED_COMPONENTS = {BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR,
 BATTLE_VIEW_ALIASES.BATTLE_TIMER,
 BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
 BATTLE_VIEW_ALIASES.BATTLE_NOTIFIER,
 DynamicAliases.FINISH_SOUND_PLAYER,
 BATTLE_VIEW_ALIASES.NEWBIE_HINT}
_FULL_MAP_HUD_STATE_COMPONENTS = {BATTLE_VIEW_ALIASES.DEBUG_PANEL, BATTLE_VIEW_ALIASES.BATTLE_MESSENGER, BATTLE_VIEW_ALIASES.FULLSCREEN_MAP}
_POSTMORTEM_HIDDEN_COMPONENTS = {BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL,
 BATTLE_VIEW_ALIASES.RIBBONS_PANEL,
 BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES,
 BATTLE_VIEW_ALIASES.VEHICLE_ERROR_MESSAGES,
 BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL}
_GUI_CONTROL_MODE_CONSUMERS = (BATTLE_VIEW_ALIASES.RADIAL_MENU, 'chat')

class PveBaseComponentsConfig(ComponentsConfig):

    def getConfig(self):
        configs = super(PveBaseComponentsConfig, self).getConfig()
        return tuple(((ctrlId, tuple((alias for alias in aliases if alias not in _REMOVED_COMPONENTS))) for ctrlId, aliases in configs))

    def __iadd__(self, other):
        resultConfig = super(PveBaseComponentsConfig, self).__iadd__(other)
        return PveBaseComponentsConfig(resultConfig.getConfig(), resultConfig.getViewsConfig())

    def __add__(self, other):
        resultConfig = super(PveBaseComponentsConfig, self).__add__(other)
        return PveBaseComponentsConfig(resultConfig.getConfig(), resultConfig.getViewsConfig())


_PVE_BASE_CONFIG = PveBaseComponentsConfig()
_COMMON_CONFIG = _PVE_BASE_CONFIG + COMMON_CLASSIC_CONFIG
_EXTENDED_CONFIG = _PVE_BASE_CONFIG + EXTENDED_CLASSIC_CONFIG

class PveBaseBattlePage(ClassicPage):

    def __init__(self, components=None, external=None, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        components = components if components is not None else (_COMMON_CONFIG if self.sessionProvider.isReplayPlaying else _EXTENDED_CONFIG)
        super(PveBaseBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        self.__isFullMapVisible = False
        self.__defaultStateVisibleComponents = set()
        self.__currentGUIConsumer = None
        self.__canToggleFullMap = False
        self.__isChatHidden = False
        return

    def _populate(self):
        super(PveBaseBattlePage, self)._populate()
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self._loadViewHandler, EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self._loadViewHandler, EVENT_BUS_SCOPE.BATTLE)
        super(PveBaseBattlePage, self)._dispose()

    def _startBattleSession(self):
        super(PveBaseBattlePage, self)._startBattleSession()
        settingsCtrl = self.sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl:
            settingsCtrl.onSettingsChanged += self._settingsChangeHandler
        self.addListener(events.GameEvent.MINIMAP_VISIBLE_CMD, self._minimapVisibleCmdHandler, scope=EVENT_BUS_SCOPE.BATTLE)

    def _stopBattleSession(self):
        self.removeListener(events.GameEvent.MINIMAP_VISIBLE_CMD, self._minimapVisibleCmdHandler, scope=EVENT_BUS_SCOPE.BATTLE)
        settingsCtrl = self.sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl:
            settingsCtrl.onSettingsChanged -= self._settingsChangeHandler
        super(PveBaseBattlePage, self)._stopBattleSession()

    def _toggleFullMap(self, isVisible):
        if self.__isFullMapVisible == isVisible:
            return
        else:
            self.__isFullMapVisible = isVisible
            visible = set(self.as_getComponentsVisibilityS())
            if isVisible:
                super(PveBaseBattlePage, self)._setComponentsVisibility(_FULL_MAP_HUD_STATE_COMPONENTS - visible, visible - _FULL_MAP_HUD_STATE_COMPONENTS)
                self.__currentGUIConsumer = BATTLE_VIEW_ALIASES.FULLSCREEN_MAP
                self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.FULLSCREEN_MAP, cursorVisible=True, enableAiming=False, stopVehicle=False)
            else:
                super(PveBaseBattlePage, self)._setComponentsVisibility(self.__defaultStateVisibleComponents - visible, visible - self.__defaultStateVisibleComponents)
                if self.__currentGUIConsumer is not None:
                    self.app.leaveGuiControlMode(self.__currentGUIConsumer)
            return

    def _setComponentsVisibility(self, visible=None, hidden=None):
        visibleAliases = self._filterExistingViewAliases(visible)
        hiddenAliases = self._filterExistingViewAliases(hidden)
        if self.__isChatHidden:
            visibleAliases.discard(BATTLE_VIEW_ALIASES.BATTLE_MESSENGER)
        self.__defaultStateVisibleComponents.update(visibleAliases)
        self.__defaultStateVisibleComponents.difference_update(hiddenAliases)
        if self.__isFullMapVisible:
            return
        super(PveBaseBattlePage, self)._setComponentsVisibility(visibleAliases, hiddenAliases)

    def _filterExistingViewAliases(self, income):
        return income - _REMOVED_COMPONENTS if income is not None else set()

    def as_isComponentVisibleS(self, componentKey):
        return super(PveBaseBattlePage, self).as_isComponentVisibleS(componentKey) if componentKey in self.components else False

    def _minimapVisibleCmdHandler(self, event):
        if not self._isVisible or not self.__canToggleFullMap:
            return
        manager = self.app.containerManager
        if manager.isModalViewsIsExists():
            return
        if event.ctx['isDown']:
            if not self.app.hasGuiControlModeConsumers(*_GUI_CONTROL_MODE_CONSUMERS):
                self._toggleFullMap(True)
        elif self.__isFullMapVisible:
            self._toggleFullMap(False)
            if self._isInPostmortem:
                self._setComponentsVisibility(hidden=_POSTMORTEM_HIDDEN_COMPONENTS, visible={BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL})

    def _settingsChangeHandler(self, settingsID):
        settingsCtrl = self.sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl is None:
            return
        else:
            if settingsID == WidgetType.MINIMAP:
                minimapSettings = settingsCtrl.getSettings(WidgetType.MINIMAP)
                if minimapSettings:
                    self.__canToggleFullMap = minimapSettings.canToggleFullMap
                    if not self.__canToggleFullMap and self.__isFullMapVisible:
                        self._toggleFullMap(False)
            elif settingsID == WidgetType.CHAT:
                chatSettings = settingsCtrl.getSettings(WidgetType.CHAT)
                if chatSettings:
                    if self.__isChatHidden != chatSettings.hide:
                        self.__isChatHidden = chatSettings.hide
                        if self.__isChatHidden:
                            _FULL_MAP_HUD_STATE_COMPONENTS.discard(BATTLE_VIEW_ALIASES.BATTLE_MESSENGER)
                            self.__defaultStateVisibleComponents.discard(BATTLE_VIEW_ALIASES.BATTLE_MESSENGER)
                            super(PveBaseBattlePage, self)._setComponentsVisibility(None, {BATTLE_VIEW_ALIASES.BATTLE_MESSENGER})
                        else:
                            _FULL_MAP_HUD_STATE_COMPONENTS.add(BATTLE_VIEW_ALIASES.BATTLE_MESSENGER)
                            self.__defaultStateVisibleComponents.add(BATTLE_VIEW_ALIASES.BATTLE_MESSENGER)
                            super(PveBaseBattlePage, self)._setComponentsVisibility({BATTLE_VIEW_ALIASES.BATTLE_MESSENGER}, None)
            elif settingsID == WidgetType.RESPAWN_HUD:
                respawnHUDSettings = settingsCtrl.getSettings(WidgetType.RESPAWN_HUD)
                if respawnHUDSettings:
                    visibilityState = 'visible' if respawnHUDSettings.showLivesInTankPanel else 'hidden'
                    self._setComponentsVisibility(**{visibilityState: {BATTLE_VIEW_ALIASES.PVE_PLAYER_LIVES}})
            return

    def _loadViewHandler(self, event):
        if event.alias == VIEW_ALIAS.INGAME_MENU:
            if self.__canToggleFullMap and self.__isFullMapVisible:
                self._toggleFullMap(False)

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        if self.__canToggleFullMap and self.__isFullMapVisible:
            self._toggleFullMap(False)
        super(PveBaseBattlePage, self)._onPostMortemSwitched(noRespawnPossible, respawnAvailable)
        self._setComponentsVisibility(hidden=_POSTMORTEM_HIDDEN_COMPONENTS, visible={BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL})

    def _onRespawnBaseMoving(self):
        super(PveBaseBattlePage, self)._onRespawnBaseMoving()
        self._setComponentsVisibility(visible=_POSTMORTEM_HIDDEN_COMPONENTS, hidden={BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL})

    def _canShowPostmortemTips(self):
        return super(PveBaseBattlePage, self)._canShowPostmortemTips() or BattleReplay.g_replayCtrl.isPlaying

    def _changeCtrlMode(self, ctrlMode):
        super(PveBaseBattlePage, self)._changeCtrlMode(ctrlMode)
        if self._isInPostmortem and ctrlMode != CTRL_MODE_NAME.POSTMORTEM:
            self._onRespawnBaseMoving()
