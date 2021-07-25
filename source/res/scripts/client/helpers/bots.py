# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/bots.py
import i18n
from constants import LocalizableBotName, BotNamingType, IS_DEVELOPMENT
from items import tankmen, vehicles
_NAME_FORMAT_CREW = ':{0} {1}:'
_DEV_PREFIX_FORMAT_CREW = '{0}_{1}_{2} '
_DEV_PREFIX_FORMAT_VEHICLE = '[{0}] '
_DEV_PREFIX_FORMAT_CUSTOM = '[{0}] '

def preprocessBotName(name):
    namingType, args = LocalizableBotName.parse(name)
    if namingType == BotNamingType.CREW_MEMBER:
        nationID, firstNameID, lastNameID = args
        nationConfig = tankmen.getNationConfig(nationID)
        firstName = i18n.convert(nationConfig.getFirstName(firstNameID))
        lastName = i18n.convert(nationConfig.getLastName(lastNameID))
        name = _NAME_FORMAT_CREW.format(firstName, lastName)
        if IS_DEVELOPMENT:
            name = _DEV_PREFIX_FORMAT_CREW.format(nationID, firstNameID, lastNameID) + name
    elif namingType == BotNamingType.VEHICLE_MODEL:
        uniqueIndex, nationID, vehicleTypeID = args
        name = i18n.convert(vehicles.g_cache.vehicle(nationID, vehicleTypeID).shortUserString)
        if IS_DEVELOPMENT:
            name = _DEV_PREFIX_FORMAT_VEHICLE.format(uniqueIndex) + name
    elif namingType == BotNamingType.CUSTOM:
        uniqueIndex, stringKey = args
        name = i18n.makeString(stringKey)
        if IS_DEVELOPMENT:
            name = _DEV_PREFIX_FORMAT_CUSTOM.format(uniqueIndex) + name
    return name
