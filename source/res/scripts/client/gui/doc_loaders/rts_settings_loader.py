# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/doc_loaders/rts_settings_loader.py
import logging
from collections import namedtuple
import typing
from ResMgr import DataSection
from bonus_readers import readBonusSection, SUPPORTED_BONUSES
from gui.server_events.bonuses import getNonQuestBonuses, splitBonuses
import resource_helper
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
_RTS_CONFIG_XML_PATH = 'gui/rts_collection_settings.xml'
_EVENT_SETTINGS = None
_EventSettings = namedtuple('_EventSettings', 'collection')
_VehicleCharacteristics = namedtuple('VehicleCharacteristics', ('pros', 'cons', 'role'))
_Portals = namedtuple('Portals', ('portalsCost',))

def _readEventSettings():
    _, section = resource_helper.getRoot(_RTS_CONFIG_XML_PATH)
    result = _EventSettings(_readCollection(section['collection']))
    resource_helper.purgeResource(_RTS_CONFIG_XML_PATH)
    return result


def _readVehicleCharacteristics(section):
    properties = frozenset(section['properties'].asString.split(' '))
    result = {}
    for subsection in section['vehicles'].values():
        vehicle = subsection['name'].asString
        result[vehicle] = _VehicleCharacteristics(_readProperties(subsection['pros'], properties), _readProperties(subsection['cons'], properties), role=subsection['role'].asString)

    return result


def _readProperties(section, allProperties):
    properties = section.asString.split(' ')
    for prop in properties:
        if prop not in allProperties:
            raise SoftException('Incorrect vehicle property "%s" in the event settings' % prop)

    return properties


def _readPortals(section):
    costs = {}
    for tag, value in section['portalsCost'].items():
        cost = value.asInt
        if cost != 1:
            raise SoftException('Cost of the {} portal must be equal to 1'.format(tag))
        costs[tag] = cost

    return _Portals(portalsCost=costs)


def _readCollection(section):
    collection = []
    for subsection in section.values():
        bonuses = []
        items = readBonusSection(SUPPORTED_BONUSES, subsection)
        for key, value in items.iteritems():
            bonuses.extend(getNonQuestBonuses(key, value))

        collection.extend(splitBonuses(bonuses))

    return collection


def getEventSettings():
    global _EVENT_SETTINGS
    if _EVENT_SETTINGS is None:
        _EVENT_SETTINGS = _readEventSettings()
    return _EVENT_SETTINGS
