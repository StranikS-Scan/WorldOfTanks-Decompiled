# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/popovers/filters/detachment_filters.py
import typing
import nations
from gui.impl.lobby.detachment.popovers import PopoverFilterGroups
from gui.impl.lobby.detachment.popovers.filters import ToggleFilters
from gui.impl.lobby.detachment.popovers.sorts import Sorts, SortType
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
ORDER = (ToggleFilters.IN_BARRACKS, ToggleFilters.ON_VEHICLE, ToggleFilters.DISMISSED)
FILTER_TO_CRITERIA = {ToggleFilters.ON_VEHICLE: REQ_CRITERIA.DETACHMENT.IN_TANK,
 ToggleFilters.IN_BARRACKS: REQ_CRITERIA.DETACHMENT.IN_BARRACKS | ~REQ_CRITERIA.DETACHMENT.DEMOBILIZE,
 ToggleFilters.DISMISSED: REQ_CRITERIA.DETACHMENT.DEMOBILIZE}

def defaultAssignmentPopoverFilters():
    return {PopoverFilterGroups.VEHICLE_TYPE: set()}


def assingmentPopoverCriteria(filters):
    criteria = REQ_CRITERIA.EMPTY
    types = filters[PopoverFilterGroups.VEHICLE_TYPE]
    if types:
        criteria |= REQ_CRITERIA.DETACHMENT.CLASSES_NAME(types)
    return criteria


def defaultBarracksPopoverFilter():
    return {PopoverFilterGroups.NATION: set(),
     PopoverFilterGroups.VEHICLE_TYPE: set()}


def defaultDetachmentToggleFilter():
    return {fName:False for fName in (ToggleFilters.IN_BARRACKS, ToggleFilters.ON_VEHICLE, ToggleFilters.DISMISSED)}


def defaultSorts():
    return {SortType.DETACHMENT: Sorts.NATION}


def barracksPopoverCriteria(filters):
    criteria = REQ_CRITERIA.EMPTY
    nationIDs = [ nations.INDICES[nation] for nation in filters.get(PopoverFilterGroups.NATION) ]
    if nationIDs:
        criteria |= REQ_CRITERIA.DETACHMENT.NATIONS(nationIDs)
    classTypes = filters.get(PopoverFilterGroups.VEHICLE_TYPE)
    if classTypes:
        criteria |= REQ_CRITERIA.DETACHMENT.CLASSES_NAME(classTypes)
    return criteria


def detachmentToggleCriteria(filters):
    if not filters:
        return REQ_CRITERIA.EMPTY
    criteria = REQ_CRITERIA.NONE
    for f in filters:
        criteria ^= FILTER_TO_CRITERIA[f]

    return criteria
