# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_control/controllers/consumables/opt_devices_ctrl.py
from gui.battle_control.controllers.consumables.opt_devices_ctrl import OptionalDevicesController
from gui.battle_control.controllers.consumables.opt_device_in_battle import DevicesSound
from fall_tanks.gui.battle_control.controllers.consumables.opt_device_sound_ctrl import FallTanksOptDevicesSounds

class FallTanksOptDevicesController(OptionalDevicesController):

    def _createSoundManager(self):
        return FallTanksOptDevicesSounds()

    def _onArenaPeriodChange(self, period, *args):
        super(FallTanksOptDevicesController, self)._onArenaPeriodChange(period, *args)
        DevicesSound.setEnabled(False)
