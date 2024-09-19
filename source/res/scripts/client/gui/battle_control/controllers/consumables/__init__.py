# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/__init__.py
from constants import ARENA_BONUS_TYPE
from gui.battle_control.controllers.consumables import ammo_ctrl, event_equipment_ctrl
from gui.battle_control.controllers.consumables import equipment_ctrl
from gui.battle_control.controllers.consumables import opt_devices_ctrl
from gui.battle_control.controllers.consumables import comp7_equipment_ctrl
_EQUIPMENT_CONTROLLERS = {ARENA_BONUS_TYPE.COMP7: comp7_equipment_ctrl.Comp7EquipmentController,
 ARENA_BONUS_TYPE.TOURNAMENT_COMP7: comp7_equipment_ctrl.Comp7EquipmentController,
 ARENA_BONUS_TYPE.TRAINING_COMP7: comp7_equipment_ctrl.Comp7EquipmentController,
 ARENA_BONUS_TYPE.EVENT_BATTLES: event_equipment_ctrl.EventEquipmentController,
 ARENA_BONUS_TYPE.EVENT_BATTLES_2: event_equipment_ctrl.EventEquipmentController}
_REPLAY_EQUIPMENT_CONTROLLERS = {ARENA_BONUS_TYPE.COMP7: comp7_equipment_ctrl.Comp7ReplayEquipmentController,
 ARENA_BONUS_TYPE.EVENT_BATTLES: event_equipment_ctrl.EventReplayConsumablesPanelMeta,
 ARENA_BONUS_TYPE.EVENT_BATTLES_2: event_equipment_ctrl.EventReplayConsumablesPanelMeta}

def extendEquipmentController(equipmentItems, replayEquipmentItems):
    _EQUIPMENT_CONTROLLERS.update(equipmentItems)
    _REPLAY_EQUIPMENT_CONTROLLERS.update(replayEquipmentItems)


def createAmmoCtrl(setup):
    if setup.isReplayRecording:
        return ammo_ctrl.AmmoReplayRecorder(setup.replayCtrl)
    return ammo_ctrl.AmmoReplayPlayer(setup.replayCtrl) if setup.isReplayPlaying else ammo_ctrl.AmmoController()


def createEquipmentCtrl(setup):
    if setup.isReplayPlaying:
        clazz = _REPLAY_EQUIPMENT_CONTROLLERS.get(setup.arenaEntity.bonusType, equipment_ctrl.EquipmentsReplayPlayer)
    else:
        clazz = _EQUIPMENT_CONTROLLERS.get(setup.arenaEntity.bonusType, equipment_ctrl.EquipmentsController)
    return clazz(setup)


def createOptDevicesCtrl(setup):
    return opt_devices_ctrl.OptionalDevicesController(setup)


__all__ = ('createAmmoCtrl', 'createEquipmentCtrl', 'createOptDevicesCtrl')
