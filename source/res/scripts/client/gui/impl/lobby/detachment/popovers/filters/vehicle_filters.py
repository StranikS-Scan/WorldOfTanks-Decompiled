# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/popovers/filters/vehicle_filters.py
from typing import Dict
from gui.impl.auxiliary.detachment_helper import hasCrewTrainedForVehicle
from gui.impl.lobby.detachment.popovers import PopoverFilterGroups
from gui.impl.lobby.detachment.popovers.filters import ToggleFilters
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
TOGGLE_FILTERS_ORDER = (ToggleFilters.IS_HAS_CREW,
 ToggleFilters.IN_HANGAR,
 ToggleFilters.NOT_IN_HANGAR,
 ToggleFilters.FAVOURITE)
FILTER_TO_CRITERIA = {ToggleFilters.IS_HAS_CREW: REQ_CRITERIA.CUSTOM(lambda v: hasCrewTrainedForVehicle(v.intCD)),
 ToggleFilters.IN_HANGAR: REQ_CRITERIA.INVENTORY,
 ToggleFilters.NOT_IN_HANGAR: ~REQ_CRITERIA.INVENTORY,
 ToggleFilters.FAVOURITE: REQ_CRITERIA.VEHICLE.FAVORITE}

def defaultVehiclePopoverFilter():
    return {PopoverFilterGroups.VEHICLE_LEVEL: set(),
     PopoverFilterGroups.VEHICLE_TYPE: set()}


def defaultVehicleToggleFilter():
    return {ToggleFilters.IS_HAS_CREW: False,
     ToggleFilters.IN_HANGAR: False,
     ToggleFilters.NOT_IN_HANGAR: False,
     ToggleFilters.FAVOURITE: False}


def toggleCriteria(filters):
    if not filters:
        return REQ_CRITERIA.EMPTY
    criteria = REQ_CRITERIA.NONE
    for f in filters:
        criteria ^= FILTER_TO_CRITERIA[f]

    return criteria


def popoverCriteria(filters):
    criteria = REQ_CRITERIA.EMPTY
    levels = filters.get(PopoverFilterGroups.VEHICLE_LEVEL)
    if levels:
        criteria |= REQ_CRITERIA.VEHICLE.LEVELS([ int(lvlStr) for lvlStr in levels ])
    types = filters.get(PopoverFilterGroups.VEHICLE_TYPE)
    if types:
        criteria |= REQ_CRITERIA.VEHICLE.CLASSES(types)
    return criteria
