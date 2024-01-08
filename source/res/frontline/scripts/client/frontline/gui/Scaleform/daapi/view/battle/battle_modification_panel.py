# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/battle/battle_modification_panel.py
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from frontline.gui.frontline_helpers import FLBattleTypeDescription
from gui.Scaleform.daapi.view.meta.EpicModificationPanelMeta import EpicModificationPanelMeta
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IEpicBattleMetaGameController

class EpicBattleModificationPanel(EpicModificationPanelMeta, IArenaVehiclesController):
    __slots__ = ('_isVisible', '_lastPeriod')
    __description = FLBattleTypeDescription()
    __epicMetaCtrl = dependency.descriptor(IEpicBattleMetaGameController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EpicBattleModificationPanel, self).__init__()
        self._isVisible = False
        self._lastPeriod = ARENA_PERIOD.IDLE

    def _populate(self):
        super(EpicBattleModificationPanel, self)._populate()
        g_playerEvents.onArenaPeriodChange += self._onRoundStarted
        self.addListener(events.GameEvent.BATTLE_LOADING, self._onBattleLoading, EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        self.removeListener(events.GameEvent.BATTLE_LOADING, self._onBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        g_playerEvents.onArenaPeriodChange -= self._onRoundStarted
        super(EpicBattleModificationPanel, self)._dispose()

    def __animationStart(self):
        self.as_setDataS(self.__getData())
        self._isVisible = True
        self.as_setVisibleS(True)

    def __animationHide(self):
        self._isVisible = False
        self.as_setVisibleS(False)

    def _onBattleLoading(self, event):
        if not event.ctx['isShown'] and not self._lastPeriod:
            self._onRoundStarted(self.__sessionProvider.shared.arenaPeriod.getPeriod())

    def _onRoundStarted(self, period, *_):
        if self._lastPeriod == period:
            return
        if self._isVisible and period == ARENA_PERIOD.BATTLE:
            self.__animationHide()
        elif not self._isVisible and period in [ARENA_PERIOD.WAITING, ARENA_PERIOD.PREBATTLE]:
            self.__animationStart()
        self._lastPeriod = period

    def __getData(self):
        return {'modificationIconPath': self.__description.getBattleTypeIconPath('c_64x64'),
         'modificationTitle': self.__description.getTitle(),
         'modificationDescription': self.__description.getShortDescription()}
