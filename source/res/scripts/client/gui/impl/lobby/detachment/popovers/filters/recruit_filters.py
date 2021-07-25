# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/popovers/filters/recruit_filters.py
import typing
import nations
from gui.impl.lobby.detachment.popovers import PopoverFilterGroups
from gui.impl.lobby.detachment.popovers.filters import ToggleFilters
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
ORDER = (ToggleFilters.IN_BARRACKS, ToggleFilters.ON_VEHICLE, ToggleFilters.DISMISSED)

def defaultRecruitPopoverFilter():
    return {PopoverFilterGroups.NATION: set(),
     PopoverFilterGroups.RECRUIT_ROLES: set(),
     PopoverFilterGroups.VEHICLE_TYPE: set()}


def defaultRecruitToggleFilter():
    return {fName:False for fName in (ToggleFilters.IN_BARRACKS, ToggleFilters.ON_VEHICLE, ToggleFilters.DISMISSED)}


FILTER_TO_CRITERIA = {ToggleFilters.ON_VEHICLE: REQ_CRITERIA.TANKMAN.IN_TANK,
 ToggleFilters.IN_BARRACKS: ~REQ_CRITERIA.TANKMAN.IN_TANK | ~REQ_CRITERIA.TANKMAN.DISMISSED,
 ToggleFilters.DISMISSED: REQ_CRITERIA.TANKMAN.DISMISSED}

def toggleCriteria(filters):
    if not filters:
        return REQ_CRITERIA.EMPTY
    criteria = REQ_CRITERIA.NONE
    for f in filters:
        criteria ^= FILTER_TO_CRITERIA[f]

    return criteria


def popoverCriteria(filters):
    criteria = REQ_CRITERIA.EMPTY
    nationIDs = [ nations.INDICES[nation] for nation in filters.get(PopoverFilterGroups.NATION) ]
    if nationIDs:
        criteria |= REQ_CRITERIA.NATIONS(nationIDs)
    roles = filters.get(PopoverFilterGroups.RECRUIT_ROLES)
    if roles:
        criteria |= REQ_CRITERIA.TANKMAN.ROLES(roles)
    vehTypes = filters.get(PopoverFilterGroups.VEHICLE_TYPE)
    if vehTypes:
        criteria |= REQ_CRITERIA.TANKMAN.NATIVE_VEH_TYPE(vehTypes)
    return criteria
