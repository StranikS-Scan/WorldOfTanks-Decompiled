# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_point_counter.py
from gui.Scaleform.daapi.view.meta.PveEventPointCounterMeta import PveEventPointCounterMeta
from game_event_getter import GameEventGetterMixin
from gui.battle_control import avatar_getter
from gui.shared.utils.graphics import isRendererPipelineDeferred
from constants import EVENT_SOULS_CHANGE_REASON

class EventPointCounter(PveEventPointCounterMeta, GameEventGetterMixin):

    def _populate(self):
        super(EventPointCounter, self)._populate()
        self.__enableAnimation()
        if self.souls is not None:
            self.souls.onSoulsChanged += self._onSoulsChanged
        self._onSoulsChanged()
        return

    def _dispose(self):
        if self.souls is not None:
            self.souls.onSoulsChanged -= self._onSoulsChanged
        super(EventPointCounter, self)._dispose()
        return

    def _onSoulsChanged(self, _=None):
        count, reason = 0, EVENT_SOULS_CHANGE_REASON.NONE
        if self.souls is not None:
            vehID = avatar_getter.getPlayerVehicleID()
            count = self.souls.getSouls(vehID)
            reason = self.souls.getLastSoulsModifiedReason(vehID)
        self.as_updateCountS(count, reason)
        return

    def __enableAnimation(self):
        self.as_enableAnimationS(isRendererPipelineDeferred())
