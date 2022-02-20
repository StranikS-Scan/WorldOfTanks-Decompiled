# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/barracks.py
import logging
from gui.Scaleform.genConsts.BARRACKS_CONSTANTS import BARRACKS_CONSTANTS
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import ITEM_TYPES, parseIntCompactDescr
from items.vehicles import VEHICLE_CLASS_TAGS
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from web.web_client_api import Field, W2CSchema, WebCommandException, w2c
from web.web_client_api.common import TManLocation
_logger = logging.getLogger(__name__)
_ALL = 'all'
_LOCATION = {TManLocation.TANKS.value: BARRACKS_CONSTANTS.LOCATION_FILTER_TANKS,
 TManLocation.BARRACKS.value: BARRACKS_CONSTANTS.LOCATION_FILTER_BARRACKS,
 _ALL: BARRACKS_CONSTANTS.LOCATION_FILTER_BARRACKS_AND_TANKS,
 TManLocation.DEMOBILIZED.value: BARRACKS_CONSTANTS.LOCATION_FILTER_DISMISSED,
 TManLocation.NEWBIES.value: BARRACKS_CONSTANTS.LOCATION_FILTER_NOT_RECRUITED}
_VEHICLE_CLASSES = frozenset(list(VEHICLE_CLASS_TAGS) + [_ALL])
_TANKMAN_ROLES = frozenset(Tankman.TANKMEN_ROLES_ORDER.keys() + [_ALL])

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _isValidTankmanLocation(_, data, itemsCache=None):
    loc = data.get('location')
    if loc in _LOCATION:
        return True
    if isinstance(loc, int):
        intCD = loc
        itemTypeID = first(parseIntCompactDescr(intCD))
        if itemTypeID != ITEM_TYPES.vehicle:
            raise WebCommandException('intCD: %d is not valid value for "location",vehicle with this descriptor are not exists', intCD)
        vehicles = itemsCache.items.getVehicles(_makeCriteria(intCD))
        if not vehicles:
            raise WebCommandException('intCD: %d is not valid value for "location",vehicle with this descriptor are not in the inventory', intCD)
        return True
    raise WebCommandException('"%s" is not valid value for "location"', loc)


def _isValidTankType(_, data):
    return _isValidParam(data, 'tank_type', _VEHICLE_CLASSES)


def _isValidTankmanRole(_, data):
    return _isValidParam(data, 'role', _TANKMAN_ROLES)


def _isValidParam(data, paramName, checkList):
    if _isOverParam(data, paramName):
        return True
    param = data.get(paramName)
    if param in checkList:
        return True
    raise WebCommandException('"%s" is not valid value for "%s"', param, paramName)


def _isOverParam(data, field):
    loc = data.get('location')
    if loc == TManLocation.NEWBIES.value:
        _logger.warning('"%s" will be ignored, is over-param for location "%s",please, simplify your W2C', field, loc)
        return True
    return False


class _BarracksTabSchema(W2CSchema):
    location = Field(required=False, type=(int, basestring), validator=_isValidTankmanLocation)
    tank_type = Field(required=False, type=basestring, validator=_isValidTankType)
    role = Field(required=False, type=basestring, validator=_isValidTankmanRole)


class BarracksWebApiMixin(object):
    __itemsCache = dependency.descriptor(IItemsCache)

    @w2c(_BarracksTabSchema, 'barracks')
    def openBarracks(self, cmd):
        location = intCD = cmd.location
        if isinstance(location, int):
            nationID, location = parseIntCompactDescr(location)[1:]
            tankType = first(self.__itemsCache.items.getVehicles(_makeCriteria(intCD)).values()).type
            role = cmd.role or _ALL
        else:
            nationID, location = None, _LOCATION.get(location)
            tankType = cmd.tank_type
            role = cmd.role
        shared_events.showBarracks(location, nationID, tankType, role)
        return


def _makeCriteria(intCD):
    return REQ_CRITERIA.INVENTORY | REQ_CRITERIA.IN_CD_LIST([intCD])
