# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_style_info/style_info_helper.py
import nations
from gui import GUI_NATIONS_ORDER_INDICES
from gui.impl.lobby.customization.shared import makeVehiclesShortNamesString
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS, VEHICLE_TYPES_ORDER
from gui.shared.gui_items.customization.c11n_items import SpecialEvents
from helpers import int2roman
from items.components.c11n_constants import CustomizationDisplayType

class Parameters(object):
    PO_ID = 'po_id'
    ICON = 'icon'
    VALUE = 'value'


TAG_TO_PO_NAME = {SpecialEvents.NY: 'ny',
 SpecialEvents.NY18: 'ny18',
 SpecialEvents.NY19: 'ny19',
 SpecialEvents.NY20: 'ny20',
 SpecialEvents.NY21: 'ny21',
 SpecialEvents.NY22: 'ny22',
 SpecialEvents.NY23: 'ny23',
 SpecialEvents.FOOTBALL18: 'football18',
 SpecialEvents.WINTER_HUNT: 'winter_hunt',
 SpecialEvents.KURSK_BATTLE: 'kursk_battle',
 SpecialEvents.HALLOWEEN: 'halloween',
 CustomizationDisplayType.HISTORICAL: 'historical',
 CustomizationDisplayType.NON_HISTORICAL: 'nonhistorical',
 CustomizationDisplayType.FANTASTICAL: 'fantastical',
 'rentable': 'rentable',
 'bonus': 'bonus'}

def getSuitable(item, currentVehicle=None):
    result = []
    for node in item.descriptor.filter.include:
        conditions = {}
        if node.nations:
            conditions['nations'] = []
            sortedNations = sorted(node.nations, key=GUI_NATIONS_ORDER_INDICES.get)
            for nation in sortedNations:
                conditions['nations'].append(nations.NAMES[nation])

        if node.tags:
            vehTypes = [ vt for vt in VEHICLE_TYPES_ORDER if vt in node.tags ]
            if vehTypes:
                conditions['vehType'] = vehTypes
            if VEHICLE_TAGS.PREMIUM in node.tags:
                conditions['isPremium'] = True
            if VEHICLE_TAGS.PREMIUM_IGR in node.tags:
                conditions['isPremiumIGR'] = True
        if node.levels:
            conditions['levels'] = []
            for level in node.levels:
                conditions['levels'].append(int2roman(level))

        if node.vehicles:
            vehicleName = makeVehiclesShortNamesString(set(node.vehicles), currentVehicle, flat=True)
            conditions['tankNames'] = vehicleName
        result.append(conditions)

    return result
