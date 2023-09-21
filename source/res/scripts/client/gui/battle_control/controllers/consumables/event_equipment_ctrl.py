# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/event_equipment_ctrl.py
import Event
from constants import WT_COMPONENT_NAMES, EQUIPMENT_STAGES
from gui.battle_control.controllers.consumables import equipment_ctrl
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared.utils.MethodsRules import MethodsRules
from items import vehicles

class EventEquipmentController(equipment_ctrl.EquipmentsController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __MAX_CHARGE = 100
    __WT_HYPERION_ITEM_NAME = 'builtinHyperion_wt'

    def __init__(self, setup):
        super(EventEquipmentController, self).__init__(setup)
        self.__charge = 0
        self.__hyperionEquipmentID = None
        self.onChargeEquipmentCounterChanged = Event.Event(self._eManager)
        self.onDebuffEquipmentChanged = Event.Event(self._eManager)
        return

    def startControl(self, *args):
        super(EventEquipmentController, self).startControl(*args)
        self.__sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
        self.__sessionProvider.onBattleSessionStop += self.__onBattleSessionStop

    def stopControl(self):
        super(EventEquipmentController, self).stopControl()
        self.__sessionProvider.onBattleSessionStart -= self.__onBattleSessionStart
        self.__sessionProvider.onBattleSessionStop -= self.__onBattleSessionStop

    @MethodsRules.delayable('notifyPlayerVehicleSet')
    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime, index=0):
        super(EventEquipmentController, self).setEquipment(intCD, quantity, stage, timeRemaining, totalTime, index)
        item = self.getEquipment(intCD)
        if item is None:
            return
        else:
            descriptor = item.getDescriptor()
            if descriptor.name == self.__WT_HYPERION_ITEM_NAME:
                if stage == EQUIPMENT_STAGES.EXHAUSTED:
                    isVisible = self.__charge < self.__MAX_CHARGE
                    self.onChargeEquipmentCounterChanged(intCD, self.__charge, isVisible)
                    self.onDebuffEquipmentChanged(intCD, item.isLocked())
            return

    def __onBattleSessionStart(self):
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onPublicCounter += self.__onPublicCounter
        self.__hyperionEquipmentID = vehicles.g_cache.equipmentIDs().get(self.__WT_HYPERION_ITEM_NAME)

    def __onBattleSessionStop(self):
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onPublicCounter -= self.__onPublicCounter
        self.__hyperionEquipmentID = None
        return

    def __onPublicCounter(self, count, maxCount, counterName):
        if counterName == WT_COMPONENT_NAMES.HYPERION_COUNTER:
            if self.__hyperionEquipmentID is None:
                return
            equipment = vehicles.g_cache.equipments()[self.__hyperionEquipmentID]
            if equipment is None:
                return
            if not self.hasEquipment(equipment.compactDescr):
                return
            item = self.getEquipment(equipment.compactDescr)
            self.__charge = count
            isExhausted = item.getStage() == EQUIPMENT_STAGES.EXHAUSTED
            isVisible = isExhausted and self.__charge < self.__MAX_CHARGE
            self.onChargeEquipmentCounterChanged(equipment.compactDescr, self.__charge, isVisible)
        return


class EventReplayConsumablesPanelMeta(equipment_ctrl.EquipmentsReplayPlayer, EventEquipmentController):
    pass
