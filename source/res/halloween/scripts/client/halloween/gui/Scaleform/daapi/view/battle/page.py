# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/page.py
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.battle.classic.page import COMMON_CLASSIC_CONFIG
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.daapi.view.battle.classic import ClassicPage
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from halloween.gui.Scaleform.daapi.view.battle.crosshair_panel_container import HalloweenCrosshairPanelContainer
from halloween.gui.Scaleform.daapi.view.battle.markers2d import HWMarkersManager
from gui.shared import EVENT_BUS_SCOPE, events
_HW_EXTERNAL_COMPONENTS = (HalloweenCrosshairPanelContainer, HWMarkersManager)
_HW_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT,
   BATTLE_VIEW_ALIASES.BATTLE_BUFF_HINT,
   BATTLE_VIEW_ALIASES.BATTLE_PICKUP_HINT,
   BATTLE_VIEW_ALIASES.BATTLE_BASE_HINT)),), viewsConfig=()) + COMMON_CLASSIC_CONFIG

class HalloweenPage(ClassicPage):

    def __init__(self, components=None, external=_HW_EXTERNAL_COMPONENTS, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        components = _HW_CONFIG if not components else components + _HW_CONFIG
        super(HalloweenPage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)

    def _populate(self):
        super(HalloweenPage, self)._populate()
        g_playerEvents.onRoundFinished += self._onRoundFinished
        self.addListener(events.GameEvent.EVENT_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        super(HalloweenPage, self)._dispose()
        g_playerEvents.onRoundFinished -= self._onRoundFinished
        self.removeListener(events.GameEvent.EVENT_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)

    def _onRespawnBaseMoving(self):
        if self._fullStatsAlias and self.as_isComponentVisibleS(self._fullStatsAlias):
            self._fsToggling.discard(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
            self._fsToggling.add(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL)
        if not self.sessionProvider.getCtx().isPlayerObserver():
            self.as_setPostmortemTipsVisibleS(False)
            self._isInPostmortem = False
        self.sessionProvider.shared.hitDirection.setVisible(True)

    def reload(self):
        hintAliases = [BATTLE_VIEW_ALIASES.BATTLE_HINT,
         BATTLE_VIEW_ALIASES.BATTLE_BUFF_HINT,
         BATTLE_VIEW_ALIASES.BATTLE_PICKUP_HINT,
         BATTLE_VIEW_ALIASES.BATTLE_BASE_HINT]
        for alias in hintAliases:
            component = self.getComponent(alias)
            if component:
                self.getComponent(alias).hideHint()

        super(HalloweenPage, self).reload()

    def _reloadPostmortem(self):
        super(HalloweenPage, self)._reloadPostmortem()
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL):
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL})

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        super(HalloweenPage, self)._onPostMortemSwitched(noRespawnPossible, respawnAvailable)
        if self._fullStatsAlias and self.as_isComponentVisibleS(self._fullStatsAlias):
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL})
            self._fsToggling.add(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
        self.sessionProvider.shared.hitDirection.setVisible(False)

    def _canShowPostmortemTips(self):
        return not self.sessionProvider.getCtx().isPlayerObserver()

    def _handleGUIToggled(self, event):
        super(HalloweenPage, self)._handleGUIToggled(event)
        if self._isVisible and not self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL):
            self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL})

    def _onRoundFinished(self, *args):
        self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, BATTLE_VIEW_ALIASES.EVENT_BASE_PANEL})
