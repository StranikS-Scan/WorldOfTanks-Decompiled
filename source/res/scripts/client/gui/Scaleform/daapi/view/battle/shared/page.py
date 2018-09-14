# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/page.py
import BattleReplay
from avatar_helpers import aim_global_binding
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.battle.shared import indicators
from gui.Scaleform.daapi.view.meta.BattlePageMeta import BattlePageMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control import g_sessionProvider, avatar_getter
from gui.battle_control.battle_constants import VIEW_COMPONENT_RULE, BATTLE_CTRL_ID
from gui.shared import EVENT_BUS_SCOPE, events
_HIT_DIRECTION_COMPONENT_ID = 'shared/hitDirection'
_SHARED_COMPONENTS_TO_CTRLS = ((BATTLE_CTRL_ID.HIT_DIRECTION, (_HIT_DIRECTION_COMPONENT_ID,)),)

class SharedPage(BattlePageMeta):

    def __init__(self, components=None):
        super(SharedPage, self).__init__()
        self._isInPostmortem = False
        self._isVisible = True
        if components is None:
            components = _SHARED_COMPONENTS_TO_CTRLS
        else:
            components += _SHARED_COMPONENTS_TO_CTRLS
        g_sessionProvider.registerViewComponents(*components)
        return

    def __del__(self):
        LOG_DEBUG('SharedPage is deleted')

    def isGuiVisible(self):
        return self._isVisible

    def _populate(self):
        super(SharedPage, self)._populate()
        self._visible = set(self.as_getComponentsVisibilityS())
        g_sessionProvider.addViewComponent(_HIT_DIRECTION_COMPONENT_ID, indicators.createDamageIndicator(), rule=VIEW_COMPONENT_RULE.NONE)
        self.addListener(events.GameEvent.RADIAL_MENU_CMD, self._handleRadialMenuCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.TOGGLE_GUI, self._handleGUIToggled, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.GLOBAL)
        ctrl = g_sessionProvider.shared.vehicleState
        if ctrl is not None:
            if ctrl.isInPostmortem:
                self.__onPostMortemSwitched()
            ctrl.onPostMortemSwitched += self.__onPostMortemSwitched
        aim_global_binding.subscribe(aim_global_binding.BINDING_ID.CTRL_MODE_NAME, self.__onAvatarCtrlModeChanged)
        return

    def _dispose(self):
        g_sessionProvider.removeViewComponent(_HIT_DIRECTION_COMPONENT_ID)
        self.removeListener(events.GameEvent.RADIAL_MENU_CMD, self._handleRadialMenuCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.TOGGLE_GUI, self._handleGUIToggled, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, EVENT_BUS_SCOPE.BATTLE)
        ctrl = g_sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
        aim_global_binding.unsubscribe(aim_global_binding.BINDING_ID.CTRL_MODE_NAME, self.__onAvatarCtrlModeChanged)
        super(SharedPage, self)._dispose()
        return

    def _toggleGuiVisible(self):
        """ Toggles GUI visible.
        NOTE: GUI visibility can not be changed in some cases. Processing of such cases is implemented
        in overridden routine _handleGUIToggled in each page.
        """
        self._isVisible = not self._isVisible
        if self._isVisible:
            self.app.containerManager.showContainers(ViewTypes.DEFAULT)
        else:
            self.app.containerManager.hideContainers(ViewTypes.DEFAULT)
        self.fireEvent(events.GameEvent(events.GameEvent.GUI_VISIBILITY, {'visible': self._isVisible}), scope=EVENT_BUS_SCOPE.BATTLE)
        avatar_getter.setComponentsVisibility(self._isVisible)

    def _setComponentsVisibility(self, visible=None, hidden=None):
        if visible is None:
            visible = set()
        if hidden is None:
            hidden = set()
        if visible or hidden:
            LOG_DEBUG('Sets components visibility', visible, hidden)
            self.as_setComponentsVisibilityS(visible, hidden)
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        g_sessionProvider.addViewComponent(alias, viewPy)

    def _onUnregisterFlashComponent(self, viewPy, alias):
        g_sessionProvider.removeViewComponent(alias)

    def _handleRadialMenuCmd(self, event):
        raise NotImplementedError

    def _handleToggleFullStats(self, event):
        raise NotImplementedError

    def _handleGUIToggled(self, event):
        raise NotImplementedError

    def _switchToPostmortem(self):
        alias = BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL
        if self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(hidden={alias})

    def __onPostMortemSwitched(self):
        if not g_sessionProvider.getCtx().isPlayerObserver() and not BattleReplay.g_replayCtrl.isPlaying:
            self.as_setPostmortemTipsVisibleS(True)
            self._isInPostmortem = True
            self._switchToPostmortem()

    def __handleShowCursor(self, _):
        self.as_toggleCtrlPressFlagS(True)

    def __handleHideCursor(self, _):
        self.as_toggleCtrlPressFlagS(False)

    def __onAvatarCtrlModeChanged(self, ctrlMode):
        if not self._isVisible:
            return
        if ctrlMode == aim_global_binding.CTRL_MODE_NAME.VIDEO:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.DAMAGE_PANEL})
        else:
            self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.DAMAGE_PANEL})
