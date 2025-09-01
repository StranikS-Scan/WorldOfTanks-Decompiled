# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/tank_setup/backports/tooltips.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.lobby.tank_setup.backports.tooltips import ConsumableToolitpBuilder
from gui.impl.backport import createTooltipData
from last_stand.gui.impl.lobby.tank_setup import LSTankSetupConstants
from LSAccountEquipmentController import getLSConsumables
LS_CONSUMABLE_EMPTY_TOOLTIP = '#last_stand.tooltips.extend:hangar/ammo_panel/ls_equipment/empty'

class LSConsumableTooltipBuilder(ConsumableToolitpBuilder):

    @classmethod
    def getEmptyTooltip(cls, *args):
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.AMMUNITION_EMPTY_SLOT, specialArgs=[LS_CONSUMABLE_EMPTY_TOOLTIP])

    @classmethod
    def getVehicle(cls, vehicle, currentSection=None):
        copyVehicle = super(LSConsumableTooltipBuilder, cls).getVehicle(vehicle, currentSection)
        if currentSection == LSTankSetupConstants.LS_CONSUMABLES:
            getLSConsumables(copyVehicle).installed = getLSConsumables(vehicle).layout.copy()
        return copyVehicle

    @classmethod
    def _getSlotItem(cls, vehicle, slotID):
        consumables = getLSConsumables(vehicle)
        return consumables.installed[int(slotID)]
