# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_phase_indicator.py
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.Scaleform.daapi.view.meta.PhaseIndicatorMeta import PhaseIndicatorMeta

def _getPhaseNumber(envID):
    return envID % 10 + 1


class EventPhaseIndicator(PhaseIndicatorMeta, GameEventGetterMixin):

    def __init__(self):
        super(EventPhaseIndicator, self).__init__()
        self._isVisible = False

    def _populate(self):
        if self.environmentData is not None:
            self.environmentData.onUpdated += self.__onEnvironmentChanged
            self.__onEnvironmentChanged()
        else:
            self._setVisible(False)
        return

    def _dispose(self):
        if self.environmentData is not None:
            self.environmentData.onUpdated -= self.__onEnvironmentChanged
        return

    def _setVisible(self, value):
        if self._isVisible != value:
            self._isVisible = value
            self.as_setVisibleS(value)

    def __onEnvironmentChanged(self):
        if not self.environmentData.hasSyncData():
            self._setVisible(False)
        else:
            self._setVisible(True)
            envID = self.__getEnvironmentId()
            maxPhase = _getPhaseNumber(self.__getEnvironmentMax())
            currentPhase = min(_getPhaseNumber(envID), maxPhase)
            self.as_setDataS(currentPhase, maxPhase)

    def __getEnvironmentId(self):
        return 0 if self.environmentData is None else self.environmentData.getCurrentEnvironmentID()

    def __getEnvironmentMax(self):
        return 0 if self.environmentData is None else self.environmentData.getMaxEnvironmentID()
