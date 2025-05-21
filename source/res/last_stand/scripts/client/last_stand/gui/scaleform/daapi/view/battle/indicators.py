# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/indicators.py
from gui.battle_control.battle_constants import HIT_INDICATOR_MAX_ON_SCREEN
from gui.Scaleform.daapi.view.battle.shared.indicators import _DamageIndicator
from gui.Scaleform.daapi.view.battle.shared.indicators import SixthSenseIndicator

class LSDamageIndicator(_DamageIndicator):
    _DAMAGE_INDICATOR_SWF = 'last_stand|lastStandBattleDamageIndicatorApp.swf'


def lsCreateDamageIndicator():
    return LSDamageIndicator(HIT_INDICATOR_MAX_ON_SCREEN)


class LSSixthSenseIndicator(SixthSenseIndicator):

    def _populate(self):
        super(LSSixthSenseIndicator, self)._populate()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self._onPostMortemSwitched
        return

    def _dispose(self):
        super(LSSixthSenseIndicator, self)._dispose()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self._onPostMortemSwitched
        return

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._cancelCallback()
        self._hide()
