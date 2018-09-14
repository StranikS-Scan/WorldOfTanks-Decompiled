# Embedded file name: scripts/client/gui/battle_control/consumables/__init__.py
from gui.battle_control.consumables.OptionalDevicesController import OptionalDevicesController
from gui.battle_control.consumables import ammo_ctrl
from gui.battle_control.consumables import equipment_ctrl

def createAmmoCtrl(isReplayPlaying, isReplayRecording):
    if isReplayRecording:
        clazz = ammo_ctrl.AmmoReplayRecorder
    elif isReplayPlaying:
        clazz = ammo_ctrl.AmmoReplayPlayer
    else:
        clazz = ammo_ctrl.AmmoController
    return clazz()


def createEquipmentCtrl(isReplayPlaying):
    if isReplayPlaying:
        clazz = equipment_ctrl.EquipmentsReplayPlayer
    else:
        clazz = equipment_ctrl.EquipmentsController
    return clazz()


def createOptDevicesCtrl():
    return OptionalDevicesController()


__all__ = ('createAmmoCtrl', 'createEquipmentCtrl', 'createOptDevicesCtrl')
