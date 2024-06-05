# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/battle_control/controllers/consumables/epic_equipment_ctrl.py
import BigWorld
from constants import EQUIPMENT_STAGES as STAGES
from frontline_common.frontline_constants import FLBattleReservesModifier
from gui.battle_control.controllers.consumables import equipment_ctrl
from gui.shared.utils.MethodsRules import MethodsRules
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class EpicEquipmentsController(equipment_ctrl.EquipmentsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, setup):
        self.slotStage = dict()
        super(EpicEquipmentsController, self).__init__(setup)

    def setServerPrevStage(self, **kwargs):
        index = kwargs.get('index', 0)
        if index > 0:
            prevStage = kwargs.get('previousStage')
            equipment = self._equipmentsIdxSlot.get(index - 1)
            if equipment and equipment[0]:
                equipment[0].setServerPrevStage(prevStage)
            return
        super(EpicEquipmentsController, self).setServerPrevStage(**kwargs)

    def cancel(self):
        for equipment in self._equipmentsIdxSlot.itervalues():
            item = equipment[0]
            if item and item.getStage() == STAGES.PREPARING and item.canDeactivate():
                item.deactivate()
                return True

        return super(EpicEquipmentsController, self).cancel()

    @MethodsRules.delayable('notifyPlayerVehicleSet')
    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime, index=0):
        index -= 1
        slot = self._equipmentsIdxSlot.get(index)
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

    @MethodsRules.delayable('notifyPlayerVehicleSet')
    def resetEquipment(self, oldIntCD, newIntCD, quantity, stage, timeRemaining, totalTime, index):
        if not oldIntCD and newIntCD:
            super(EpicEquipmentsController, self).setEquipment(newIntCD, quantity, stage, timeRemaining, totalTime, index)
        else:
            super(EpicEquipmentsController, self).resetEquipment(oldIntCD, newIntCD, quantity, stage, timeRemaining, totalTime, index)


class EpicReplayEquipmentController(EpicEquipmentsController):
    __slots__ = ('__callbackID', '__callbackTimeID', '__percentGetters', '__percents', '__timeGetters', '__times')

    def __init__(self, setup):
        super(EpicReplayEquipmentController, self).__init__(setup)
        self.__callbackID = None
        self.__callbackTimeID = None
        self.__percentGetters = {}
        self.__percents = {}
        self.__timeGetters = {}
        self.__times = {}
        return

    def getEquipmentKey(self, intCD, index):
        return (intCD, index)

    def getEquipmentByKey(self, key):
        if not isinstance(key, tuple):
            return None
        else:
            intCD, index = key
            return self.getEquipmentByIDx(index - 1) if index > 0 else self.getEquipment(intCD)

    def clear(self, leave=True):
        arenaDP = self.sessionProvider.getArenaDP()
        if leave:
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            if self.__callbackTimeID is not None:
                BigWorld.cancelCallback(self.__callbackTimeID)
                self.__callbackTimeID = None
            self.__percents.clear()
            self.__percentGetters.clear()
            self.__times.clear()
            self.__timeGetters.clear()
        elif arenaDP is None or arenaDP.getReservesModifier() != FLBattleReservesModifier.RANDOM:
            for idx, equipment in enumerate(self._equipmentsIdxSlot.itervalues()):
                key = self.getEquipmentKey(equipment[1], idx + 1)
                self.__percents.pop(key, None)
                self.__percentGetters.pop(key, None)
                self.__times.pop(key, None)
                self.__timeGetters.pop(key, None)

        super(EpicReplayEquipmentController, self).clear(leave)
        return

    @MethodsRules.delayable('notifyPlayerVehicleSet')
    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime, index=0):
        super(EpicReplayEquipmentController, self).setEquipment(intCD, quantity, stage, timeRemaining, totalTime, index)
        self.__resetTimers(intCD, stage, index)

    @MethodsRules.delayable('notifyPlayerVehicleSet')
    def resetEquipment(self, oldIntCD, newIntCD, quantity, stage, timeRemaining, totalTime, index):
        super(EpicReplayEquipmentController, self).resetEquipment(oldIntCD, newIntCD, quantity, stage, timeRemaining, totalTime, index)
        if oldIntCD:
            oldKey = self.getEquipmentKey(oldIntCD, index)
            self.__percents.pop(oldKey, None)
            self.__percentGetters.pop(oldKey, None)
            self.__times.pop(oldKey, None)
            self.__timeGetters.pop(oldKey, None)
        self.__resetTimers(newIntCD, stage, index)
        return

    @classmethod
    def createItem(cls, descriptor, quantity, stage, timeRemaining, totalTime):
        item = cls._findExtendItem(True, descriptor.name, descriptor, quantity, stage, timeRemaining, totalTime)
        if item:
            return item
        tags, clazz = equipment_ctrl._getInitialTagsAndClass(descriptor, equipment_ctrl._REPLAY_EQUIPMENT_TAG_TO_ITEM)
        if tags:
            item = clazz(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        else:
            item = equipment_ctrl._ReplayItem(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        return item

    def getActivationCode(self, intCD, entityName=None, avatar=None):
        return None

    def canActivate(self, intCD, entityName=None, avatar=None):
        return (False, None)

    def changeSetting(self, intCD, entityName=None, avatar=None, idx=None):
        return (False, None)

    def changeSettingByTag(self, tag, entityName=None, avatar=None):
        return (False, None)

    def __resetTimers(self, intCD, stage, index):
        key = self.getEquipmentKey(intCD, index)
        self.__percents.pop(key, None)
        self.__percentGetters.pop(key, None)
        self.__times.pop(key, None)
        self.__timeGetters.pop(key, None)
        equipment = self.getEquipmentByKey(key)
        if not equipment:
            return
        else:
            if stage in (STAGES.DEPLOYING,
             STAGES.COOLDOWN,
             STAGES.SHARED_COOLDOWN,
             STAGES.ACTIVE) or stage == STAGES.READY and equipment.getTimeRemaining():
                self.__percentGetters[key] = equipment.getCooldownPercents
                if self.__callbackID is not None:
                    BigWorld.cancelCallback(self.__callbackID)
                    self.__callbackID = None
                if equipment.getTotalTime() > 0:
                    self.__timeGetters[key] = equipment.getReplayTimeRemaining
                    if self.__callbackTimeID is not None:
                        BigWorld.cancelCallback(self.__callbackTimeID)
                        self.__callbackTimeID = None
                self.__timeLoop()
                self.__timeLoopInSeconds()
            return

    def __timeLoop(self):
        self.__callbackID = None
        self.__tick()
        self.__callbackID = BigWorld.callback(0.1, self.__timeLoop)
        return

    def __timeLoopInSeconds(self):
        self.__callbackTimeID = None
        self.__tickInSeconds()
        self.__callbackTimeID = BigWorld.callback(1, self.__timeLoopInSeconds)
        return

    def __tick(self):
        for key, percentGetter in self.__percentGetters.iteritems():
            percent = percentGetter()
            currentPercent = self.__percents.get(key)
            if currentPercent != percent:
                self.__percents[key] = percent
                self.onEquipmentCooldownInPercent(key, percent)

    def __tickInSeconds(self):
        for key, timeGetter in self.__timeGetters.iteritems():
            time = timeGetter()
            currentTime = self.__times.get(key)
            if currentTime != time:
                equipment = self.getEquipmentByKey(key)
                if not equipment:
                    return
                intCD, _ = key
                isBaseTime = self._equipments.has_key(intCD) and equipment.getStage() == STAGES.ACTIVE
                self.__times[key] = time
                self.onEquipmentCooldownTime(key, time, isBaseTime, time == 0)
