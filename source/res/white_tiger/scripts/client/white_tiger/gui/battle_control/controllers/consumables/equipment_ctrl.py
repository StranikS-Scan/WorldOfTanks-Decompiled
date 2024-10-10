# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/consumables/equipment_ctrl.py
import Event
from constants import WT_COMPONENT_NAMES, EQUIPMENT_STAGES
from gui.battle_control.controllers.consumables.equipment_ctrl import EquipmentsReplayPlayer, EquipmentsController
from gui.shared.utils.MethodsRules import MethodsRules
from helpers import dependency
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import ARENA_PERIOD
from cgf_components import wt_helpers

class WhiteTigerEquipmentController(EquipmentsController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __MAX_CHARGE = 100
    __WT_HYPERION_ITEM_NAME = 'builtinHyperion_wt'

    def __init__(self, setup):
        super(WhiteTigerEquipmentController, self).__init__(setup)
        self.__charge = 0
        self.__hyperionEquipmentID = None
        self.onChargeEquipmentCounterChanged = Event.Event(self._eManager)
        self.onDebuffEquipmentChanged = Event.Event(self._eManager)
        return

    def startControl(self, *args):
        super(WhiteTigerEquipmentController, self).startControl(*args)
        self.__sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
        self.__sessionProvider.onBattleSessionStop += self.__onBattleSessionStop

    def stopControl(self):
        super(WhiteTigerEquipmentController, self).stopControl()
        self.__sessionProvider.onBattleSessionStart -= self.__onBattleSessionStart
        self.__sessionProvider.onBattleSessionStop -= self.__onBattleSessionStop

    @MethodsRules.delayable('notifyPlayerVehicleSet')
    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime):
        super(WhiteTigerEquipmentController, self).setEquipment(intCD, quantity, stage, timeRemaining, totalTime)
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

    def getEquipment(self, intCD):
        periodCtrl = self.__sessionProvider.shared.arenaPeriod
        if periodCtrl and periodCtrl.getPeriod() <= ARENA_PERIOD.WAITING:
            return
        else:
            try:
                item = self._equipments[intCD]
            except KeyError:
                item = None

            return item

    def __onPublicCounter(self, count, maxCount, counterName):
        periodCtrl = self.__sessionProvider.shared.arenaPeriod
        if periodCtrl and periodCtrl.getPeriod() <= ARENA_PERIOD.WAITING:
            return
        else:
            if counterName == WT_COMPONENT_NAMES.HYPERION_COUNTER and wt_helpers.isBoss():
                if self.__hyperionEquipmentID is None:
                    return
                equipment = vehicles.g_cache.equipments()[self.__hyperionEquipmentID]
                if equipment is None:
                    return
                item = self.getEquipment(equipment.compactDescr)
                if item is None:
                    return
                self.__charge = count
                isExhausted = item.getStage() == EQUIPMENT_STAGES.EXHAUSTED
                isVisible = isExhausted and self.__charge < self.__MAX_CHARGE
                self.onChargeEquipmentCounterChanged(equipment.compactDescr, self.__charge, isVisible)
            return


class WhiteTigerReplayConsumablesPanelMeta(EquipmentsReplayPlayer, WhiteTigerEquipmentController):
    pass
