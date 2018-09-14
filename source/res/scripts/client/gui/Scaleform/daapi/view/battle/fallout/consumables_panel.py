# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/fallout/consumables_panel.py
import rage
from gui.Scaleform.daapi.view.meta.FalloutConsumablesPanelMeta import FalloutConsumablesPanelMeta
from gui.battle_control import g_sessionProvider

class FalloutConsumablesPanel(FalloutConsumablesPanelMeta):

    def __init__(self):
        super(FalloutConsumablesPanel, self).__init__()
        self.__hasRage = False
        self.__currentValue = 0

    def _populate(self):
        super(FalloutConsumablesPanel, self)._populate()
        self.__hasRage = g_sessionProvider.arenaVisitor.hasRage()
        if self.__hasRage:
            self._startRage()

    def _dispose(self):
        if self.__hasRage:
            self._stopRage()
        super(FalloutConsumablesPanel, self)._dispose()

    def _startRage(self):
        vehicleCtrl = g_sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
        avatarStatsCtrl = g_sessionProvider.shared.privateStats
        if avatarStatsCtrl is not None:
            avatarStatsCtrl.onUpdated += self.__onAvatarStatsUpdated
            self.__currentValue = avatarStatsCtrl.getStats().get('ragePoints', 0)
            barProps = {'maxValue': rage.g_cache.pointsLimit,
             'curValue': self.__currentValue}
            self.as_initializeRageProgressS(True, barProps)
        return

    def _stopRage(self):
        avatarStatsCtrl = g_sessionProvider.shared.privateStats
        if avatarStatsCtrl is not None:
            avatarStatsCtrl.onUpdated -= self.__onAvatarStatsUpdated
        vehicleCtrl = g_sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        return

    def __onRespawnBaseMoving(self):
        assert self.__hasRage, 'Unexpected event'
        self.as_updateProgressBarValueS(self.__currentValue)

    def __onAvatarStatsUpdated(self, stats):
        assert self.__hasRage, 'Unexpected event'
        newValue = stats.get('ragePoints', 0)
        if newValue == self.__currentValue:
            return
        delta = newValue - self.__currentValue
        if delta < 0:
            self.as_updateProgressBarValueS(newValue)
        else:
            self.as_updateProgressBarValueByDeltaS(delta)
        self.__currentValue = newValue
