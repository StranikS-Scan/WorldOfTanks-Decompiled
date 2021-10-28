# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_ribbons_panel.py
import logging
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import BattleRibbonsPanel, _RIBBONS_FMTS
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.shared import EVENT_BUS_SCOPE, events
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES as _BET
_logger = logging.getLogger(__name__)

class EventRibbonsPanel(BattleRibbonsPanel, GameEventGetterMixin):

    def __init__(self):
        super(EventRibbonsPanel, self).__init__()
        self.addListener(events.GameEvent.COLLECTOR_PROGRESS, self._onCollectorProgress, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.COLLECTOR_PROGRESS_STOP, self._onCollectorProgressStop, scope=EVENT_BUS_SCOPE.BATTLE)
        self._isRibbonPanelOverlay = False

    def _populate(self):
        super(EventRibbonsPanel, self)._populate()
        if self.environmentData is not None:
            self.environmentData.onUpdated += self.__onEnvironmentChanged
            self.__onEnvironmentChanged()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self._onPostMortemSwitched
        return

    def _dispose(self):
        self.removeListener(events.GameEvent.COLLECTOR_PROGRESS, self._onCollectorProgress, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.COLLECTOR_PROGRESS_STOP, self._onCollectorProgressStop, scope=EVENT_BUS_SCOPE.BATTLE)
        if self.environmentData is not None:
            self.environmentData.onUpdated -= self.__onEnvironmentChanged
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self._onPostMortemSwitched
        super(EventRibbonsPanel, self)._dispose()
        return

    def _checkUserPreferences(self, ribbon):
        return not self._isRibbonPanelOverlay if ribbon.getType() in _BET.BUFFS_SET or ribbon.getType() in _BET.EVENT_SET else super(EventRibbonsPanel, self)._checkUserPreferences(ribbon)

    def _invalidateRibbon(self, ribbon, method):
        arenaDP = self.sessionProvider.getCtx().getArenaDP()
        if self._shouldShowRibbon(ribbon) and not self._isRibbonPanelOverlay:
            if ribbon.getType() in _RIBBONS_FMTS:
                updater = _RIBBONS_FMTS[ribbon.getType()]
                updater(ribbon, arenaDP, method)
            else:
                _logger.error('Could not find formatter for ribbon %s', ribbon)

    def _onCollectorProgress(self, event):
        ribbonOverlays = event.ctx.get('overlays', {}).get('isRibbonsPanelOverlay', False)
        self._isRibbonPanelOverlay = ribbonOverlays

    def _onCollectorProgressStop(self, _):
        self._isRibbonPanelOverlay = False

    def _clearPanel(self):
        self.as_resetS()
        self._getRibbonsAggregator().clearRibbonsData()

    def __onEnvironmentChanged(self):
        self._clearPanel()

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._clearPanel()
