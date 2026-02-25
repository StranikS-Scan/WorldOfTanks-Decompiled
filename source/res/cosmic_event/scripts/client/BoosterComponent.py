# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/BoosterComponent.py
import Event
from script_component.DynamicScriptComponent import DynamicScriptComponent
from cosmic_event_common_cgf.boosters.components import BoosterComponent as BoosterComponentBase
from cosmic_event_common_cgf.boosters.constants import BoosterType

class BoosterComponent(DynamicScriptComponent, BoosterComponentBase):
    onBoardStateChanged = Event.Event()
    onGeyserStateChanged = Event.Event()
    onBoardApply = Event.Event()
    onGeyserApply = Event.Event()

    @property
    def go(self):
        return self.entity.entityGameObject

    def set_isActive(self, prev):
        if self.type == BoosterType.BOARD:
            self.onBoardStateChanged(self.entity.position, self.isActive)
        elif self.type == BoosterType.GEYSER:
            self.onGeyserStateChanged(self.entity.position, self.isActive)

    def set_boosterApplyTime(self, prev):
        if self.type == BoosterType.BOARD:
            self.onBoardApply(self.go, self.entity.position)
        elif self.type == BoosterType.GEYSER:
            self.onGeyserApply(self.go, self.entity.position)
