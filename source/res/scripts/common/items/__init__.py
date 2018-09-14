# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/__init__.py
import ResMgr
from items import _xml
from constants import IS_CLIENT, ITEM_DEFS_PATH
if IS_CLIENT:
    from helpers import i18n
ITEM_TYPE_NAMES = ('reserved', 'vehicle', 'vehicleChassis', 'vehicleTurret', 'vehicleGun', 'vehicleEngine', 'vehicleFuelTank', 'vehicleRadio', 'tankman', 'optionalDevice', 'shell', 'equipment')
MAX_ITEM_TYPE_INDEX = len(ITEM_TYPE_NAMES) - 1

class ITEM_TYPES(dict):

    def __init__(self):
        for idx, name in enumerate(ITEM_TYPE_NAMES):
            if name != 'reserved':
                self[name] = idx
                setattr(self, name, idx)


ITEM_TYPES = ITEM_TYPES()
ITEM_TYPE_INDICES = dict(((x[1], x[0]) for x in enumerate(ITEM_TYPE_NAMES) if x[1] != 'reserved'))
SIMPLE_ITEM_TYPE_NAMES = ('vehicleChassis', 'vehicleTurret', 'vehicleGun', 'vehicleEngine', 'vehicleFuelTank', 'vehicleRadio', 'optionalDevice', 'shell', 'equipment')
SIMPLE_ITEM_TYPE_INDICES = tuple((ITEM_TYPE_INDICES[x] for x in SIMPLE_ITEM_TYPE_NAMES))
VEHICLE_ATTRIBUTE_FACTORS = {'engine/power': 1.0,
 'turret/rotationSpeed': 1.0,
 'circularVisionRadius': 1.0,
 'invisibility': [0.0, 1.0],
 'radio/distance': 1.0,
 'gun/rotationSpeed': 1.0,
 'chassis/shotDispersionFactors/movement': 1.0,
 'gun/shotDispersionFactors/turretRotation': 1.0,
 'gun/reloadTime': 1.0,
 'gun/aimingTime': 1.0,
 'gun/canShoot': True,
 'engine/fireStartingChance': 1.0,
 'healthBurnPerSecLossFraction': 1.0,
 'repairSpeed': 1.0,
 'brokenTrack': None,
 'vehicle/rotationSpeed': 1.0,
 'chassis/terrainResistance': [1.0, 1.0, 1.0],
 'ramming': 1.0,
 'crewLevelIncrease': 0,
 'crewChanceToHitFactor': 1.0}
VEHICLE_COMPONENT_TYPE_NAMES = ('vehicleChassis', 'vehicleTurret', 'vehicleGun', 'vehicleEngine', 'vehicleFuelTank', 'vehicleRadio')
VEHICLE_COMPONENT_TYPE_INDICES = tuple((ITEM_TYPE_INDICES[x] for x in VEHICLE_COMPONENT_TYPE_NAMES))

def init(preloadEverything, pricesToCollect = None):
    global _g_itemTypes
    _g_itemTypes = _readItemTypes()
    from items import vehicles
    vehicles.init(preloadEverything, pricesToCollect)
    from items import tankmen
    tankmen.init(preloadEverything)
    from . import qualifiers
    qualifiers.init()


def getTypeInfoByName(typeName):
    return _g_itemTypes[typeName]


def getTypeInfoByIndex(typeIndex):
    return _g_itemTypes[ITEM_TYPE_NAMES[typeIndex]]


def getTypeOfCompactDescr(compactDescr):
    if type(compactDescr) is int:
        typeID = compactDescr & 15
    else:
        typeID = ord(compactDescr[0]) & 15
    if typeID >= len(ITEM_TYPE_NAMES):
        raise Exception, "is not a 'compact descriptor'"
    return typeID


def _readItemTypes():
    xmlPath = ITEM_DEFS_PATH + 'item_types.xml'
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    res = {}
    for index, name in enumerate(ITEM_TYPE_NAMES):
        if name == 'reserved':
            continue
        itemSection = _xml.getSubsection(xmlCtx, section, name)
        ctx = (xmlCtx, name)
        tagNames = []
        tags = {}
        if itemSection.has_key('tags'):
            for tagSection in itemSection['tags'].values():
                tagName = intern(tagSection.name)
                if tags.has_key(tagName):
                    _xml.raiseWrongXml(xmlCtx, 'tags' + tagName, 'tag name is not unique')
                tagDescr = {'name': tagName,
                 'index': len(tagNames)}
                if IS_CLIENT:
                    tagDescr['userString'] = i18n.makeString(tagSection.readString('userString'))
                    tagDescr['description'] = i18n.makeString(tagSection.readString('description'))
                tags[tagName] = tagDescr
                tagNames.append(tagName)

        descr = {'index': index,
         'tags': tags,
         'tagNames': tuple(tagNames)}
        if IS_CLIENT:
            descr['userString'] = i18n.makeString(itemSection.readString('userString'))
            descr['description'] = i18n.makeString(itemSection.readString('description'))
        res[name] = descr

    section = None
    itemSection = None
    tagSection = None
    ResMgr.purge(xmlPath, True)
    return res
