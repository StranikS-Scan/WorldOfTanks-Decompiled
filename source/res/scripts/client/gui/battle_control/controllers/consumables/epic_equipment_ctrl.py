# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/epic_equipment_ctrl.py
from gui.battle_control.controllers.consumables import equipment_ctrl
from constants import EQUIPMENT_STAGES as STAGES
from gui.shared.utils.MethodsRules import MethodsRules
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_TYPE_CAPS
from skeletons.gui.game_control import IEpicBattleMetaGameController
from helpers import dependency

class EpicEquipmentsController(equipment_ctrl.EquipmentsController):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, setup):
        self.slotStage = dict()
        super(EpicEquipmentsController, self).__init__(setup)

    def cancel(self):
        if not self.__epicController.hasBonusCap(BONUS_TYPE_CAPS.EPIC_RANDOM_RESERVES):
            return super(EpicEquipmentsController, self).cancel()
        for equipment in self._equipmentsIdxSlot.itervalues():
            item = equipment[0]
            if item and item.getStage() == STAGES.PREPARING and item.canDeactivate():
                item.deactivate()
                return True

        return False

    @MethodsRules.delayable('notifyPlayerVehicleSet')
    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime, index=0):
        index -= 1
        slot = self._equipmentsIdxSlot.get(index, None)
        slotIdx = len(self._equipmentsIdxSlot)
        if stage == STAGES.WAIT_FOR_CHOICE:
            if slot and slot[3] == stage:
                return
            self._equipmentsIdxSlot[index] = (0,
             0,
             slotIdx,
             stage)
            idx = index if index > 0 else 0
            self.onSlotWaited(idx, quantity)
        elif intCD == 0 and stage == STAGES.UNAVAILABLE:
            if slot and slot[3] == stage:
                return
            self._equipmentsIdxSlot[index] = (0,
             0,
             slotIdx,
             stage)
            self.onSlotBlocked(index)
        else:
            super(EpicEquipmentsController, self).setEquipment(intCD, quantity, stage, timeRemaining, totalTime, index + 1)
        return

    @MethodsRules.delayable('notifyPlayerVehicleSet')
    def resetEquipment(self, oldIntCD, newIntCD, quantity, stage, timeRemaining, totalTime, index):
        if not oldIntCD and newIntCD:
            super(EpicEquipmentsController, self).setEquipment(newIntCD, quantity, stage, timeRemaining, totalTime, index)
        else:
            super(EpicEquipmentsController, self).resetEquipment(oldIntCD, newIntCD, quantity, stage, timeRemaining, totalTime, index)


class EpicReplayEquipmentController(EpicEquipmentsController, equipment_ctrl.EquipmentsReplayPlayer):
    pass
