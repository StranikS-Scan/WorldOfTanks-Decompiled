# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/vehicle_config_types_readers.py
from items import _xml
import vehicle_config_types

def readLodDist(xmlCtx, section, subsectionName):
    from items.vehicles import g_cache
    name = _xml.readNonEmptyString(xmlCtx, section, subsectionName)
    dist = g_cache.commonConfig['lodLevels'].get(name)
    if dist is None:
        _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown lod level '%s'" % name)
    return dist


def readLodSettings(xmlCtx, section):
    return vehicle_config_types.LodSettings(readLodDist(xmlCtx, section, 'lodSettings/maxLodDistance'), _xml.readIntOrNone(xmlCtx, section, 'lodSettings/maxPriority'))
