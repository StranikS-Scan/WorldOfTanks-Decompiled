# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/indicators.py
from gui.Scaleform.daapi.view.battle.shared.indicators import SixthSenseIndicator

class HalloweenSixthSenseIndicator(SixthSenseIndicator):

    def _populate(self):
        super(HalloweenSixthSenseIndicator, self)._populate()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self._onPostMortemSwitched
        return

    def _dispose(self):
        super(HalloweenSixthSenseIndicator, self)._dispose()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self._onPostMortemSwitched
        return

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._cancelCallback()
        self._hide()
