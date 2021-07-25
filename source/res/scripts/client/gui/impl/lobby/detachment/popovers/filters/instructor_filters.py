# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/popovers/filters/instructor_filters.py
import typing
import nations
from gui.impl.lobby.detachment.popovers import PopoverFilterGroups
from gui.impl.lobby.detachment.popovers.filters import ToggleFilters
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
TOGGLE_FILTERS_ORDER = (ToggleFilters.CREW, ToggleFilters.IN_BARRACKS, ToggleFilters.REMOVED)
FILTER_TO_CRITERIA = {ToggleFilters.CREW: REQ_CRITERIA.INSTRUCTOR.ASSIGNED_TO_DETACHMENT,
 ToggleFilters.IN_BARRACKS: REQ_CRITERIA.INSTRUCTOR.IN_BARRACKS,
 ToggleFilters.TOKEN: REQ_CRITERIA.INSTRUCTOR.TOKENS,
 ToggleFilters.REMOVED: REQ_CRITERIA.INSTRUCTOR.EXCLUDED}

def defaultInstructorToggleFilter():
    return {fName:False for fName in TOGGLE_FILTERS_ORDER}


def defaultInstructorPopoverFilter():
    return {PopoverFilterGroups.NATION: set(),
     PopoverFilterGroups.INSTRUCTOR_CLASS: set()}


def toggleCriteria(filters):
    if not filters:
        return REQ_CRITERIA.EMPTY
    criteria = REQ_CRITERIA.NONE
    for f in filters:
        criteria ^= FILTER_TO_CRITERIA[f]

    return criteria


def popoverCriteria(filters):
    criteria = REQ_CRITERIA.EMPTY
    nationIDs = [ nations.INDICES[nation] for nation in filters[PopoverFilterGroups.NATION] ]
    if nationIDs:
        criteria |= REQ_CRITERIA.INSTRUCTOR.NATIONS(nationIDs)
    classes = [ int(i) for i in filters[PopoverFilterGroups.INSTRUCTOR_CLASS] ]
    if classes:
        criteria |= REQ_CRITERIA.INSTRUCTOR.CLASSES_ID(classes)
    return criteria
