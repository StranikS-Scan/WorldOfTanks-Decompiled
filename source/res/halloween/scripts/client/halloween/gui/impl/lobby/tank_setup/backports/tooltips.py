# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tank_setup/backports/tooltips.py
from __future__ import absolute_import
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.tank_setup.backports.tooltips import ConsumableToolitpBuilder
from gui.impl.backport import createTooltipData
from halloween.gui.impl.lobby.tank_setup import HWTankSetupConstants
HW_CONSUMABLE_EMPTY_TOOLTIP = '#halloween.tooltips.extend:hangar/ammo_panel/hw_equipment/empty'

class HWConsumableTooltipBuilder(ConsumableToolitpBuilder):

    @classmethod
    def getEmptyTooltip(cls, *args):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AMMUNITION_EMPTY_SLOT, specialArgs=[HW_CONSUMABLE_EMPTY_TOOLTIP])

    @classmethod
    def getVehicle(cls, vehicle, currentSection=None):
        copyVehicle = super(HWConsumableTooltipBuilder, cls).getVehicle(vehicle, currentSection)
        if currentSection == HWTankSetupConstants.HW_CONSUMABLES:
            copyVehicle.consumables.setInstalled(*vehicle.consumables.layout)
        else:
            copyVehicle.consumables.setInstalled(*vehicle.consumables.installed)
        return copyVehicle
