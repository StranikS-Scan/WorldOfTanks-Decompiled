# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/consumables/white_tiger_equipment_ctrl.py
import Event
from gui.battle_control.controllers.consumables import equipment_ctrl
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from items import vehicles
from white_tiger.cgf_components.wt_helpers import getBattleStateComponent
from white_tiger.cgf_components import wt_helpers, wt_sound_helpers
from PlayerEvents import g_playerEvents
from math_utils import clamp

class WhiteTigerEquipmentController(equipment_ctrl.EquipmentsController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __MAX_CHARGE = 100
    __WT_HYPERION_ITEM_NAME = 'builtinHyperion_wt'

    def __init__(self, setup):
        super(WhiteTigerEquipmentController, self).__init__(setup)
        self.__charge = 0
        self.__hyperionEquipmentID = None
        self.__eManager = Event.EventManager()
        self.onChargeEquipmentCounterChanged = Event.Event(self.__eManager)
        self.onDebuffEquipmentChanged = Event.Event(self._eManager)
        self.__hyperionChargeDirty = 0
        return

    def startControl(self, *args):
        super(WhiteTigerEquipmentController, self).startControl(*args)
        self.__sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
        self.__sessionProvider.onBattleSessionStop += self.__onBattleSessionStop
        g_playerEvents.onAvatarReady += self.__onAvatarReady

    def stopControl(self):
        super(WhiteTigerEquipmentController, self).stopControl()
        self.__sessionProvider.onBattleSessionStart -= self.__onBattleSessionStart
        self.__sessionProvider.onBattleSessionStop -= self.__onBattleSessionStop
        g_playerEvents.onAvatarReady -= self.__onAvatarReady

    def __onAvatarReady(self):
        battleStateComponent = getBattleStateComponent()
        if battleStateComponent:
            battleStateComponent.onHyperionCharge += self.__onHyperionCharge

    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime, index=0):
        timeRemaining = clamp(0, totalTime, timeRemaining)
        super(WhiteTigerEquipmentController, self).setEquipment(intCD, quantity, stage, timeRemaining, totalTime, index)
        item = self.getEquipment(intCD)
        if item is None:
            return
        else:
            descriptor = item.getDescriptor()
            if descriptor.name == self.__WT_HYPERION_ITEM_NAME:
                if wt_helpers.isHyperionCharging(stage):
                    isVisible = self.__charge < self.__MAX_CHARGE
                    self.onChargeEquipmentCounterChanged(intCD, self.__charge, isVisible)
                    self.onDebuffEquipmentChanged(intCD, item.isLocked())
            if self.__hyperionChargeDirty != 0:
                self.__onHyperionCharge(self.__hyperionChargeDirty)
            return

    def __onBattleSessionStart(self):
        self.__hyperionEquipmentID = vehicles.g_cache.equipmentIDs().get(self.__WT_HYPERION_ITEM_NAME)

    def __onBattleSessionStop(self):
        self.__hyperionEquipmentID = None
        return

    def __onHyperionCharge(self, charge):
        if self.__hyperionEquipmentID is None:
            return
        else:
            equipment = vehicles.g_cache.equipments()[self.__hyperionEquipmentID]
            if equipment is None:
                return
            if not self.hasEquipment(equipment.compactDescr):
                self.__hyperionChargeDirty = charge
                return
            self.__hyperionChargeDirty = 0
            item = self.getEquipment(equipment.compactDescr)
            self.__charge = charge
            isExhausted = wt_helpers.isHyperionCharging(item.getStage())
            isVisible = isExhausted and self.__charge < self.__MAX_CHARGE
            self.onChargeEquipmentCounterChanged(equipment.compactDescr, self.__charge, isVisible)
            return


class WhiteTigerReplayConsumablesPanelMeta(equipment_ctrl.EquipmentsReplayPlayer, WhiteTigerEquipmentController):
    pass


class WTEquipmentSound(equipment_ctrl.EquipmentSound):

    @staticmethod
    def playPressed(item, result):
        equipment = vehicles.g_cache.equipments()[item.getEquipmentID()]
        if equipment is not None:
            sound = equipment.soundPressedReady if result else equipment.soundPressedNotReady
            if sound is not None:
                wt_sound_helpers.play2d(sound)
        return

    @staticmethod
    def playCancel(item):
        equipment = vehicles.g_cache.equipments()[item.getEquipmentID()]
        if equipment is not None:
            sound = equipment.soundPressedCancel
            if sound is not None:
                wt_sound_helpers.play2d(sound)
        return


__all__ = ('WhiteTigerEquipmentController', 'WhiteTigerReplayConsumablesPanelMeta')
