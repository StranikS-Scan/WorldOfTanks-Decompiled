# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/crew_books_tab.py
from gui.Scaleform.daapi.view.lobby.storage.inventory.filters.filter_by_nation import FiltrableInventoryCategoryByNationTabView
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from items.components.crew_books_constants import CREW_BOOK_RARITY
from shared_utils import CONST_CONTAINER
from skeletons.gui.lobby_context import ILobbyContext

class _CrewBooksFilterBit(CONST_CONTAINER):
    RARE_1 = 1
    RARE_2 = 2
    RARE_3 = 4
    PERSONAL = 8


_TYPE_FILTER_ITEMS = [{'filterValue': _CrewBooksFilterBit.RARE_1,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.CREWBOOKS_STORAGE_FILTERS_BROCHURE_TITLE),
  'icon': RES_ICONS.MAPS_ICONS_STORAGE_FILTERS_ICON_BUTTON_RARE_1},
 {'filterValue': _CrewBooksFilterBit.RARE_2,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.CREWBOOKS_STORAGE_FILTERS_GUIDE_TITLE),
  'icon': RES_ICONS.MAPS_ICONS_STORAGE_FILTERS_ICON_BUTTON_RARE_2},
 {'filterValue': _CrewBooksFilterBit.RARE_3,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.CREWBOOKS_STORAGE_FILTERS_CREWBOOK_TITLE),
  'icon': RES_ICONS.MAPS_ICONS_STORAGE_FILTERS_ICON_BUTTON_RARE_3},
 {'filterValue': _CrewBooksFilterBit.PERSONAL,
  'selected': False,
  'tooltip': makeTooltip(body=TOOLTIPS.CREWBOOKS_STORAGE_FILTERS_PERSONALBOOK_TITLE),
  'icon': RES_ICONS.MAPS_ICONS_STORAGE_FILTERS_ICON_BUTTON_PERSONAL}]
_TYPE_ID_BIT_TO_TYPE_ID_MAP = {_CrewBooksFilterBit.RARE_1: CREW_BOOK_RARITY.CREW_COMMON,
 _CrewBooksFilterBit.RARE_2: CREW_BOOK_RARITY.CREW_RARE,
 _CrewBooksFilterBit.RARE_3: CREW_BOOK_RARITY.CREW_EPIC,
 _CrewBooksFilterBit.PERSONAL: CREW_BOOK_RARITY.PERSONAL}

class CrewBooksTabView(FiltrableInventoryCategoryByNationTabView):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    filterItems = _TYPE_FILTER_ITEMS

    def _getClientSectionKey(self):
        pass

    def _getItemTypeID(self):
        return GUI_ITEM_TYPE.CREW_BOOKS

    def _getFilteredCriteria(self):
        criteria = super(CrewBooksTabView, self)._getFilteredCriteria() | REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT
        kindsList = [ _TYPE_ID_BIT_TO_TYPE_ID_MAP[bit] for bit in _TYPE_ID_BIT_TO_TYPE_ID_MAP.iterkeys() if self._filterMask & bit ]
        if kindsList:
            criteria |= REQ_CRITERIA.CREW_ITEM.BOOK_RARITIES(kindsList)
        return criteria

    def _getRequestCriteria(self, invVehicles):
        return REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT
