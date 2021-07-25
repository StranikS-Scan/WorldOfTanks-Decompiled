# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/popovers/filters/commander_filters.py
import typing
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_card_constants import CommanderCardConstants
from gui.impl.lobby.detachment.popovers import PopoverFilterGroups, CommanderToggleTypes
from gui.impl.lobby.detachment.popovers.filters import ToggleFilters
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
from gui.shared.utils.requesters.ItemsRequester import PredicateCondition
from shared_utils import CONST_CONTAINER
ORDER = (ToggleFilters.SKINS, ToggleFilters.DOCUMENTS)

class PortraitTypes(CONST_CONTAINER):
    DOCUMENT = 'document'
    SKIN = 'skin'


POPOVER_FILTER_TO_CRITERIA = {CommanderToggleTypes.HISTORICAL: RequestCriteria(PredicateCondition(lambda item: item.type in (CommanderCardConstants.COMMANDER_TYPE_HISTORICAL, CommanderCardConstants.COMMANDER_TYPE_DEFAULT))),
 CommanderToggleTypes.NON_HISTORICAL: RequestCriteria(PredicateCondition(lambda item: item.type in (CommanderCardConstants.COMMANDER_TYPE_NON_HISTORICAL, CommanderCardConstants.COMMANDER_TYPE_DEFAULT))),
 CommanderToggleTypes.USED: RequestCriteria(PredicateCondition(lambda item: item.portraitType == PortraitTypes.DOCUMENT or item.isUsed))}

def popoverCriteria(filters):
    criteria = REQ_CRITERIA.EMPTY
    nations = filters.get(PopoverFilterGroups.NATION)
    if nations:
        criteria |= RequestCriteria(PredicateCondition(lambda item: item.nation in nations or item.nation == ''))
    for f in filters.get(PopoverFilterGroups.COMMANDER_TYPE):
        criteria |= POPOVER_FILTER_TO_CRITERIA[f]

    return criteria


FILTER_TO_CRITERIA = {ToggleFilters.SKINS: RequestCriteria(PredicateCondition(lambda item: item.portraitType == PortraitTypes.SKIN)),
 ToggleFilters.DOCUMENTS: RequestCriteria(PredicateCondition(lambda item: item.portraitType == PortraitTypes.DOCUMENT))}

def toggleCriteria(filters):
    if not filters:
        return REQ_CRITERIA.EMPTY
    criteria = REQ_CRITERIA.NONE
    for f in filters:
        criteria ^= FILTER_TO_CRITERIA[f]

    return criteria


def defaultCommanderPopoverFilter():
    return {PopoverFilterGroups.NATION: set(),
     PopoverFilterGroups.COMMANDER_TYPE: set()}


def defaultCommanderToggleFilter():
    return {f:False for f in ToggleFilters.ALL()}
