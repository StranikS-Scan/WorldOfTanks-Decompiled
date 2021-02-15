# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/__init__.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from gui.battle_control.controllers.consumables import ammo_ctrl
from gui.battle_control.controllers.consumables import equipment_ctrl
from gui.battle_control.controllers.consumables import opt_devices_ctrl
from gui.battle_control.controllers.consumables import br_equipment_ctrl

def createAmmoCtrl(setup):
    if setup.isReplayRecording:
        return ammo_ctrl.AmmoReplayRecorder(setup.replayCtrl)
    return ammo_ctrl.AmmoReplayPlayer(setup.replayCtrl) if setup.isReplayPlaying else ammo_ctrl.AmmoController()


def createEquipmentCtrl(setup):
    isBattleRoyale = ARENA_BONUS_TYPE_CAPS.checkAny(setup.arenaEntity.bonusType, ARENA_BONUS_TYPE_CAPS.BATTLEROYALE)
    if setup.isReplayPlaying:
        clazz = br_equipment_ctrl.SteelHunterReplayEquipmentController if isBattleRoyale else equipment_ctrl.EquipmentsReplayPlayer
    elif isBattleRoyale:
        clazz = br_equipment_ctrl.SteelHunterEquipmentController
    else:
        clazz = equipment_ctrl.EquipmentsController
    return clazz(setup)


def createOptDevicesCtrl(setup):
    return opt_devices_ctrl.OptionalDevicesController(setup)


__all__ = ('createAmmoCtrl', 'createEquipmentCtrl', 'createOptDevicesCtrl')
