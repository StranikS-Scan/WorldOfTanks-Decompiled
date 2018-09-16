# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/respawn/respawn_utils.py
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
import BigWorld
from helpers import i18n
from helpers import time_utils
from gui import makeHtmlString
FLAG_ICON_TEMPLATE = '../maps/icons/battle/respawn/optimize_flags_160x100/%s.png'
VEHICLE_TYPE_TEMPLATE = '../maps/icons/vehicleTypes/%s.png'
VEHICLE_TYPE_ELITE_TEMPLATE = '../maps/icons/vehicleTypes/elite/%s.png'
VEHICLE_LEVEL_TEMPLATE = '../maps/icons/levels/tank_level_%d.png'
VEHICLE_FORMAT = makeHtmlString('html_templates:igr/premium-vehicle', 'name', {})
VEHICLE_TYPE_BIG_TEMPLATE = '../maps/icons/vehicleTypes/big/%s.png'
VEHICLE_ELITE_TYPE_TEMPLATE = '../maps/icons/vehicleTypes/elite/%s.png'

def getVehicleName(vehicle):
    tags = vehicle.type.tags
    isIGR = bool(VEHICLE_TAGS.PREMIUM_IGR in tags)
    vehicleName = vehicle.type.shortUserString if isIGR else vehicle.type.userString
    if isIGR:
        vehicleName = VEHICLE_FORMAT % {'vehicle': vehicleName}
    return vehicleName


def getSlotsStatesData(vehsList, cooldowns, disabled, limits={}):
    result = []
    for v in vehsList:
        compactDescr = v.intCD
        cooldownTime = cooldowns.get(compactDescr, 0)
        cooldownStr = ''
        cooldown = cooldownTime - BigWorld.serverTime()
        enabled = cooldown <= 0 and not disabled and compactDescr not in limits
        if not enabled:
            if cooldownTime is not 0:
                if disabled:
                    cooldownStr = i18n.makeString('#ingame_gui:respawnView/disabledLbl')
                else:
                    cooldownStr = i18n.makeString('#ingame_gui:respawnView/cooldownLbl', time=time_utils.getTimeLeftFormat(cooldown))
            else:
                cooldownStr = i18n.makeString('#ingame_gui:respawnView/classNotAvailable')
        result.append({'vehicleID': compactDescr,
         'enabled': enabled,
         'cooldown': cooldownStr,
         'settings': v.settings})

    return result
