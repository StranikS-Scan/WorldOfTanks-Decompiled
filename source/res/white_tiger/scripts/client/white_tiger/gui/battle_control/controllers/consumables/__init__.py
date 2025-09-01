# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/consumables/__init__.py
from white_tiger_common.wt_constants import ARENA_BONUS_TYPE
from gui.battle_control.controllers.consumables import ammo_ctrl
from gui.battle_control.controllers.consumables import opt_devices_ctrl
from white_tiger.gui.battle_control.controllers.consumables import white_tiger_equipment_ctrl
_EQUIPMENT_CONTROLLERS = {ARENA_BONUS_TYPE.WHITE_TIGER: white_tiger_equipment_ctrl.WhiteTigerEquipmentController}
_REPLAY_EQUIPMENT_CONTROLLERS = {ARENA_BONUS_TYPE.WHITE_TIGER: white_tiger_equipment_ctrl.WhiteTigerReplayConsumablesPanelMeta}

def extendEquipmentController(equipmentItems, replayEquipmentItems):
    _EQUIPMENT_CONTROLLERS.update(equipmentItems)
    _REPLAY_EQUIPMENT_CONTROLLERS.update(replayEquipmentItems)


def createAmmoCtrl(setup):
    if setup.isReplayRecording:
        return ammo_ctrl.AmmoReplayRecorder(setup.replayCtrl)
    return ammo_ctrl.AmmoReplayPlayer(setup.replayCtrl) if setup.isReplayPlaying else ammo_ctrl.AmmoController()


def createEquipmentCtrl(setup):
    if setup.isReplayPlaying:
        clazz = _REPLAY_EQUIPMENT_CONTROLLERS.get(setup.arenaEntity.bonusType, white_tiger_equipment_ctrl.WhiteTigerReplayConsumablesPanelMeta)
    else:
        clazz = _EQUIPMENT_CONTROLLERS.get(setup.arenaEntity.bonusType, white_tiger_equipment_ctrl.WhiteTigerEquipmentController)
    return clazz(setup)


def createOptDevicesCtrl(setup):
    return opt_devices_ctrl.OptionalDevicesController(setup)


__all__ = ('createAmmoCtrl', 'createEquipmentCtrl', 'createOptDevicesCtrl')
