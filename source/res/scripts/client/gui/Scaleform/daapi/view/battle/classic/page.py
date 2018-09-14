# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/page.py
from AvatarInputHandler.aih_constants import CTRL_MODE_NAME
from constants import ARENA_PERIOD
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.battle.shared import SharedPage
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
_CLASSIC_COMPONENTS_TO_CTRLS = ((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
   BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
   BATTLE_VIEW_ALIASES.PLAYERS_PANEL,
   BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL)), (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL,)), (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)))

class ClassicPage(SharedPage):

    def __init__(self, components=_CLASSIC_COMPONENTS_TO_CTRLS, external=None, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        self._fullStatsAlias = fullStatsAlias
        super(ClassicPage, self).__init__(components=components, external=external)

    def __del__(self):
        LOG_DEBUG('ClassicPage is deleted')

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

    def _toggleFullStats(self, isShown, permanent=None):
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
            if self.as_isComponentVisibleS(self._fullStatsAlias) != isShown:
                if isShown:
                    if len(self._fsToggling) == 0:
                        self._fsToggling = set(self.as_getComponentsVisibilityS())
                    if permanent is not None:
                        self._fsToggling.difference_update(permanent)
                    self._setComponentsVisibility(visible={self._fullStatsAlias}, hidden=self._fsToggling)
                else:
                    self._setComponentsVisibility(visible=self._fsToggling, hidden={self._fullStatsAlias})
                    self._fsToggling.clear()
                if self._isInPostmortem:
                    self.as_setPostmortemTipsVisibleS(not isShown)
            return

    def _handleRadialMenuCmd(self, event):
        isDown = event.ctx['isDown']
        self._toggleRadialMenu(isDown)

    def _handleToggleFullStats(self, event):
        self._toggleFullStats(event.ctx['isDown'])

    def _onBattleLoadingStart(self):
        self._toggleFullStats(False)
        super(ClassicPage, self)._onBattleLoadingStart()

    def _onBattleLoadingFinish(self):
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

    def _changeCtrlMode(self, ctrlMode):
        if ctrlMode == CTRL_MODE_NAME.VIDEO:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.DAMAGE_PANEL, BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL})
        else:
            self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.DAMAGE_PANEL, BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL})
