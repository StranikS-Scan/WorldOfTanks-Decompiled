# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/battle_pickup_hint.py
from helpers import dependency
from gui.Scaleform.daapi.view.meta.BattleHintMeta import BattleHintMeta
from gui.battle_control.controllers.battle_hints_ctrl import BattleHintComponent
from skeletons.gui.battle_session import IBattleSessionProvider

class BattlePickupHint(BattleHintComponent, BattleHintMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattlePickupHint, self).__init__()
        self._isRespawning = False
        self._showed = False

    def _populate(self):
        super(BattlePickupHint, self)._populate()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self._onPostMortemSwitched
            ctrl.onRespawnBaseMoving += self._onRespawnBaseMoving
        return

    def _dispose(self):
        super(BattlePickupHint, self)._dispose()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self._onPostMortemSwitched
            ctrl.onRespawnBaseMoving -= self._onRespawnBaseMoving
        return

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._hideHint()
        self._isRespawning = True

    def _onRespawnBaseMoving(self):
        self._isRespawning = False

    def _showHint(self, data):
        if self._isRespawning:
            return
        self._showed = True
        self.as_showHintS(data)

    def _hideHint(self):
        if not self._showed:
            return
        self._showed = False
        self.as_hideHintS()
