# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/__init__.py
from gui.battle_control.controllers.consumables import ammo_ctrl
from gui.battle_control.controllers.consumables import equipment_ctrl
from gui.battle_control.controllers.consumables import opt_devices_ctrl

def createAmmoCtrl(setup):
    if setup.isReplayRecording:
        return ammo_ctrl.AmmoReplayRecorder(setup.replayCtrl)
    return ammo_ctrl.AmmoController() if setup.isReplayPlaying else ammo_ctrl.AmmoController()


def createEquipmentCtrl(setup):
    if setup.isReplayPlaying:
        clazz = equipment_ctrl.EquipmentsReplayPlayer
    else:
        clazz = equipment_ctrl.EquipmentsController
    return clazz()


def createOptDevicesCtrl():
    return opt_devices_ctrl.OptionalDevicesController()


__all__ = ('createAmmoCtrl', 'createEquipmentCtrl', 'createOptDevicesCtrl')
