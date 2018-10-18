# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/page.py
from account_helpers.AccountSettings import AccountSettings, EVENT_INTRO_SHOW_COUNT
from gui.Scaleform.daapi.view.battle.event.container import PveCrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.event.indicators import PveDamageIndicator
from gui.Scaleform.daapi.view.battle.event.manager import PveMarkersManager
from gui.Scaleform.daapi.view.battle.shared import SharedPage, period_music_listener
from gui.Scaleform.daapi.view.battle.event.event_finish_sound_player import EventFinishSoundPlayer
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES as _ALIASES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.battle_constants import HIT_INDICATOR_MAX_ON_SCREEN
from gui.shared import events, EVENT_BUS_SCOPE
from shared_utils import CONST_CONTAINER
_INTRO_SHOW_COUNT_LIMIT = 2

class DynamicAliases(CONST_CONTAINER):
    FINISH_SOUND_PLAYER = 'finishSoundPlayer'
    PERIOD_MUSIC_LISTENER = 'periodMusicListener'


def createDamageIndicator():
    return PveDamageIndicator(HIT_INDICATOR_MAX_ON_SCREEN)


class _EventComponentsConfig(ComponentsConfig):

    def __init__(self):
        introShowCount = AccountSettings.getSettings(EVENT_INTRO_SHOW_COUNT)
        showIntro = introShowCount < _INTRO_SHOW_COUNT_LIMIT
        introConfig = tuple()
        if showIntro:
            AccountSettings.setSettings(EVENT_INTRO_SHOW_COUNT, introShowCount + 1)
            introConfig = (_ALIASES.EVENT_INTRO,)
        super(_EventComponentsConfig, self).__init__(((BATTLE_CTRL_ID.ARENA_PERIOD, (_ALIASES.BATTLE_TIMER,
           _ALIASES.BATTLE_END_WARNING_PANEL,
           _ALIASES.PREBATTLE_TIMER,
           DynamicAliases.PERIOD_MUSIC_LISTENER,
           DynamicAliases.FINISH_SOUND_PLAYER) + introConfig),
         (BATTLE_CTRL_ID.TEAM_BASES, (DynamicAliases.FINISH_SOUND_PLAYER,)),
         (BATTLE_CTRL_ID.EVENTPOINTS_VIEW, (_ALIASES.EVENT_POINT_COUNTER, _ALIASES.EVENT_POINT_CURRENT)),
         (BATTLE_CTRL_ID.BATTLE_HINTS, (_ALIASES.EVENT_BATTLE_HINT,)),
         (BATTLE_CTRL_ID.DEBUG, (_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.HIT_DIRECTION, (_ALIASES.HIT_DIRECTION,)),
         (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.FINISH_SOUND_PLAYER,))), ((_ALIASES.HIT_DIRECTION, createDamageIndicator), (DynamicAliases.PERIOD_MUSIC_LISTENER, period_music_listener.PeriodMusicListener), (DynamicAliases.FINISH_SOUND_PLAYER, EventFinishSoundPlayer)))


_PVE_EXTERNAL_COMPONENTS = (PveCrosshairPanelContainer, PveMarkersManager)

class EventBattlePage(SharedPage):

    def __init__(self, components=None, external=_PVE_EXTERNAL_COMPONENTS):
        components = (components or ComponentsConfig()) + _EventComponentsConfig()
        self._inactiveComponents = set()
        super(EventBattlePage, self).__init__(components=components, external=external)

    def _populate(self):
        add = self.addListener
        add(events.GameEvent.HIDE_HUD_COMPONENTS, self._hideHudComponents, scope=EVENT_BUS_SCOPE.BATTLE)
        add(events.GameEvent.SHOW_HUD_COMPONENTS, self._showHudComponents, scope=EVENT_BUS_SCOPE.BATTLE)
        add(events.GameEvent.SHOW_EXTERNAL_COMPONENTS, self.__handleShowExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        add(events.GameEvent.HIDE_EXTERNAL_COMPONENTS, self.__handleHideExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        super(EventBattlePage, self)._populate()

    def _dispose(self):
        remove = self.removeListener
        remove(events.GameEvent.HIDE_HUD_COMPONENTS, self._hideHudComponents, scope=EVENT_BUS_SCOPE.BATTLE)
        remove(events.GameEvent.SHOW_HUD_COMPONENTS, self._showHudComponents, scope=EVENT_BUS_SCOPE.BATTLE)
        remove(events.GameEvent.SHOW_EXTERNAL_COMPONENTS, self.__handleShowExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        remove(events.GameEvent.HIDE_EXTERNAL_COMPONENTS, self.__handleHideExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self._inactiveComponents.clear()
        super(EventBattlePage, self)._dispose()

    def _setComponentsVisibility(self, visible=None, hidden=None):
        if visible is not None:
            visible.discard(_ALIASES.RADIAL_MENU)
        if hidden is not None and _ALIASES.RADIAL_MENU in hidden:
            self._toggleRadialMenu(False)
        super(EventBattlePage, self)._setComponentsVisibility(visible, hidden)
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(EventBattlePage, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == _ALIASES.RIBBONS_PANEL:
            viewPy.setSoundsEnabled(False)

    def _hideHudComponents(self, event):
        self._inactiveComponents.update(set(event.ctx))
        self._setComponentsVisibility(hidden=event.ctx)

    def _showHudComponents(self, event):
        self._inactiveComponents.difference_update(set(event.ctx))
        self._setComponentsVisibility(visible=event.ctx)

    def _handleToggleFullStats(self, event):
        pass

    def _handleToggleFullStatsQuestProgress(self, event):
        pass

    def _handleGUIToggled(self, event):
        self._toggleGuiVisible()

    def _handleRadialMenuCmd(self, event):
        isDown = event.ctx['isDown']
        self._toggleRadialMenu(isDown)

    def _changeCtrlMode(self, ctrlMode):
        pass

    def _switchToPostmortem(self):
        super(EventBattlePage, self)._switchToPostmortem()
        if self.as_isComponentVisibleS(_ALIASES.RADIAL_MENU):
            self._toggleRadialMenu(False)

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        pass

    def _reloadPostmortem(self):
        pass

    def _onBattleLoadingFinish(self):
        super(EventBattlePage, self)._onBattleLoadingFinish()
        self._setComponentsVisibility(hidden={_ALIASES.DAMAGE_PANEL, _ALIASES.MINIMAP, _ALIASES.RIBBONS_PANEL})

    def _toggleRadialMenu(self, isShown):
        manager = self.app.containerManager
        if _ALIASES.RADIAL_MENU in self._inactiveComponents and isShown:
            return
        elif not manager.isContainerShown(ViewTypes.DEFAULT):
            return
        elif manager.isModalViewsIsExists():
            return
        else:
            radialMenu = self.getComponent(_ALIASES.RADIAL_MENU)
            if radialMenu is None:
                return
            if isShown:
                radialMenu.show()
                self.app.enterGuiControlMode(_ALIASES.RADIAL_MENU, cursorVisible=False, enableAiming=False)
            else:
                self.app.leaveGuiControlMode(_ALIASES.RADIAL_MENU)
                radialMenu.hide()
            return

    def __handleShowExternals(self, _):
        ctrl = self.sessionProvider.shared.eventController
        ctrl.setMarkersVisible(True)

    def __handleHideExternals(self, _):
        ctrl = self.sessionProvider.shared.eventController
        ctrl.setMarkersVisible(False)
