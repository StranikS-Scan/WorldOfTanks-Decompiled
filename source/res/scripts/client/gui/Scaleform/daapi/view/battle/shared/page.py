# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/page.py
import BattleReplay
from AvatarInputHandler import aih_constants, aih_global_binding
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.battle.shared import crosshair
from gui.Scaleform.daapi.view.battle.shared import indicators
from gui.Scaleform.daapi.view.battle.shared import markers2d
from gui.Scaleform.daapi.view.meta.BattlePageMeta import BattlePageMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES as _ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VIEW_COMPONENT_RULE, BATTLE_CTRL_ID
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_SHARED_COMPONENTS_TO_CTRLS = ((BATTLE_CTRL_ID.HIT_DIRECTION, (_ALIASES.HIT_DIRECTION,)),)

class SharedPage(BattlePageMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, components=None, external=None):
        super(SharedPage, self).__init__()
        self._isInPostmortem = False
        self._isVisible = True
        self._blToggling = set()
        self._fsToggling = set()
        if external is None:
            external = (crosshair.CrosshairPanelContainer, markers2d.MarkersManager)
        self._external = [ item() for item in external ]
        if components is None:
            components = _SHARED_COMPONENTS_TO_CTRLS
        else:
            components += _SHARED_COMPONENTS_TO_CTRLS
        self.__components = components
        return

    def __del__(self):
        LOG_DEBUG('SharedPage is deleted')

    def isGuiVisible(self):
        return self._isVisible

    def reload(self):
        """Reloads (destroys and create again) all components, because replay destroys all entities,
        all controllers when player rewinds replay back.
        """
        self._stopBattleSession()
        self.__onPostMortemReload()
        self._startBattleSession()
        self.reloadComponents()
        for component in self._external:
            component.startPlugins()

    def _populate(self):
        self._startBattleSession()
        super(SharedPage, self)._populate()
        for component in self._external:
            component.setOwner(self.app)

        self.addListener(events.GameEvent.RADIAL_MENU_CMD, self._handleRadialMenuCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.TOGGLE_GUI, self._handleGUIToggled, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        self.fireEvent(events.GlobalSpaceEvent(events.GlobalSpaceEvent.GO_NEXT))

    def _dispose(self):
        while len(self._external):
            component = self._external.pop()
            component.close()

        self.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.RADIAL_MENU_CMD, self._handleRadialMenuCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.TOGGLE_GUI, self._handleGUIToggled, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, scope=EVENT_BUS_SCOPE.GLOBAL)
        self._stopBattleSession()
        super(SharedPage, self)._dispose()

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
        self.sessionProvider.addViewComponent(alias, viewPy)

    def _onUnregisterFlashComponent(self, viewPy, alias):
        self.sessionProvider.removeViewComponent(alias)

    def _startBattleSession(self):
        """This method is invoked when battle starts, because method _populate
        is not invoked in replay when player rewinds replay back."""
        self.sessionProvider.registerViewComponents(*self.__components)
        self.sessionProvider.addViewComponent(_ALIASES.HIT_DIRECTION, indicators.createDamageIndicator(), rule=VIEW_COMPONENT_RULE.NONE)
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            if ctrl.isInPostmortem:
                self.__onPostMortemSwitched()
            ctrl.onPostMortemSwitched += self.__onPostMortemSwitched
        aih_global_binding.subscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self.__onAvatarCtrlModeChanged)
        return

    def _stopBattleSession(self):
        """This method is invoked when battle stops."""
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
        aih_global_binding.unsubscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self.__onAvatarCtrlModeChanged)
        self.sessionProvider.removeViewComponent(_ALIASES.HIT_DIRECTION)
        for component in self._external:
            component.stopPlugins()

        return

    def _handleRadialMenuCmd(self, event):
        raise NotImplementedError

    def _handleToggleFullStats(self, event):
        raise NotImplementedError

    def _handleGUIToggled(self, event):
        raise NotImplementedError

    def _onBattleLoadingStart(self):
        if len(self._blToggling) == 0:
            self._blToggling = set(self.as_getComponentsVisibilityS())
        self._blToggling.difference_update([_ALIASES.BATTLE_LOADING])
        self._blToggling.add(_ALIASES.BATTLE_MESSENGER)
        self._setComponentsVisibility(visible={_ALIASES.BATTLE_LOADING}, hidden=self._blToggling)

    def _onBattleLoadingFinish(self):
        self._setComponentsVisibility(visible=self._blToggling, hidden={_ALIASES.BATTLE_LOADING})
        self._blToggling.clear()
        for component in self._external:
            component.active(True)

    def _changeCtrlMode(self, ctrlMode):
        if ctrlMode == ctrlMode == aih_constants.CTRL_MODE_NAME.VIDEO:
            self._setComponentsVisibility(hidden={_ALIASES.DAMAGE_PANEL})
        else:
            self._setComponentsVisibility(visible={_ALIASES.DAMAGE_PANEL})

    def __handleBattleLoading(self, event):
        if event.ctx['isShown']:
            self._onBattleLoadingStart()
        else:
            self._onBattleLoadingFinish()

    def _switchToPostmortem(self):
        alias = _ALIASES.CONSUMABLES_PANEL
        if self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(hidden={alias})

    def _reloadPostmortem(self):
        alias = _ALIASES.CONSUMABLES_PANEL
        if not self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(visible={alias})

    def __onPostMortemSwitched(self):
        if not self.sessionProvider.getCtx().isPlayerObserver() and not BattleReplay.g_replayCtrl.isPlaying:
            self.as_setPostmortemTipsVisibleS(True)
        if not self.sessionProvider.getCtx().isPlayerObserver():
            self._isInPostmortem = True
            self._switchToPostmortem()

    def __onPostMortemReload(self):
        self._isInPostmortem = False
        self._reloadPostmortem()

    def __handleShowCursor(self, _):
        self.as_toggleCtrlPressFlagS(True)

    def __handleHideCursor(self, _):
        self.as_toggleCtrlPressFlagS(False)

    def __onAvatarCtrlModeChanged(self, ctrlMode):
        if not self._isVisible or len(self._fsToggling) > 0 or len(self._blToggling) > 0:
            return
        self._changeCtrlMode(ctrlMode)


class BattlePageBusinessHandler(PackageBusinessHandler):
    """Uses this handler to load page for playing replay correctly."""
    __slots__ = ()

    def __init__(self, *aliases):
        listeners = [ (alias, self.__loadPage) for alias in aliases ]
        super(BattlePageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def __loadPage(self, event):
        page = self.findViewByAlias(ViewTypes.DEFAULT, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return
