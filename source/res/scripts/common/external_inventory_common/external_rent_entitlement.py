# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/external_inventory_common/external_rent_entitlement.py
from items import vehicles
EXTERNAL_RENT_ENTITLEMENT_PREFIX = 'ext_rent'

def isExternalRentEntitlement(entitlementCode):
    return entitlementCode.startswith(EXTERNAL_RENT_ENTITLEMENT_PREFIX)


def parseEntitlement(entitlementCode):
    if not isExternalRentEntitlement(entitlementCode):
        return (False, None, 'Wrong prefix')
    else:
        tokens = entitlementCode.split(':')
        if len(tokens) < 3:
            return (False, None, 'Wrong amount of tokens')
        vehName = tokens[1] + ':' + tokens[2]
        if not vehicles.g_list.isVehicleExisting(vehName):
            return (False, None, 'Unknown vehicle')
        nationID, innationID = vehicles.g_list.getIDsByName(vehName)
        vehTypeCompDescr = vehicles.makeIntCompactDescrByID('vehicle', nationID, innationID)
        partnerCode = None
        if len(tokens) >= 4:
            partnerCode = tokens[3]
        data = {'vehTypeCompDescr': vehTypeCompDescr,
         'partnerCode': partnerCode}
        return (True, data, '')
