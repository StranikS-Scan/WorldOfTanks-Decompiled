# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/custom/collector20.py
import ResMgr
import typing
from items.vehicles import makeVehicleTypeCompDescrByName
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import FrozenSet
    VehCD = int
COLLECTOR20_CONFIG_PATH = 'scripts/item_defs/collector20.xml'
CONFIG_SECTION = 'collector20Vehicles'
COLLECTOR20_MEDAL_ID = 'twoPointZeroCollectorMedal'
COLLECTOR20_BADGE_IDS = (215, 216)
_g_collector20Config = frozenset()

def _readConfig():
    section = ResMgr.openSection(COLLECTOR20_CONFIG_PATH)
    if section is None:
        raise SoftException('Collector20 vehicles config is not found at %s!' % COLLECTOR20_CONFIG_PATH)
    vehiclesSection = section[CONFIG_SECTION]
    if vehiclesSection is None:
        raise SoftException('%s section is not found in %s!' % (CONFIG_SECTION, COLLECTOR20_CONFIG_PATH))
    result = set()
    vehicleNames = vehiclesSection.readString('').split()
    for vehicleName in vehicleNames:
        vehTypeCompDescr = makeVehicleTypeCompDescrByName(vehicleName)
        if vehTypeCompDescr in result:
            raise SoftException('%r specified more than once in %s!' % (vehicleName, COLLECTOR20_CONFIG_PATH))
        result.add(vehTypeCompDescr)

    return frozenset(result)


def loadCollector20Config():
    global _g_collector20Config
    if not _g_collector20Config:
        _g_collector20Config = _readConfig()


def getCollector20Config():
    if not _g_collector20Config:
        loadCollector20Config()
    return _g_collector20Config
