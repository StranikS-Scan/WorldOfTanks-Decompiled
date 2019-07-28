# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_hangar/vo_converters.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from items import vehicles
from gui.shared.utils.functions import makeTooltip
FITTING_SLOTS = (GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.OPTIONALDEVICE],)

def makeVehicleVo(vehicle):
    _, vehicleName = vehicle.name.split(':', 1)
    return {'vehicleIcon': '../maps/shop/vehicles/180x135/{0}.png'.format(vehicleName),
     'icon': RES_ICONS.maps_icons_vehicletypes_all_png(vehicle.type),
     'label': vehicle.userName}


def makeAmmoVO(shells):
    outcome = []
    for shell in shells:
        if shell.isHidden:
            continue
        outcome.append({'icon': '../maps/icons/ammopanel/ammo/%s' % shell.descriptor.icon[0],
         'label': shell.longUserNameAbbr,
         'specialAlias': TOOLTIPS_CONSTANTS.HANGAR_SHELL,
         'isSpecial': True,
         'specialArgs': [str(shell.intCD)]})

    return outcome


def makeAbbilityVO(abilityID, emptyLabel=False, isHangar=False):
    itemDescr = vehicles.g_cache.equipments()[abilityID]
    iconName = itemDescr.iconName
    if isHangar:
        icon = RES_ICONS.getGeneralAbilityIconInHangar(iconName)
    else:
        icon = RES_ICONS.getGeneralAbilityIcon(iconName)
    return {'icon': icon,
     'label': '' if emptyLabel else itemDescr.shortUserString,
     'description': itemDescr.description,
     'tooltip': makeTooltip(itemDescr.userString, itemDescr.description)}
