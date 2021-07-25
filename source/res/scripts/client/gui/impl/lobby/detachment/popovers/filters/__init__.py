# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/popovers/filters/__init__.py
from gui.impl.gen import R
from shared_utils import CONST_CONTAINER

class ToggleFilters(CONST_CONTAINER):
    IN_BARRACKS = 'inBarracks'
    ON_VEHICLE = 'onVehicle'
    DISMISSED = 'dismissed'
    CREW = 'crew'
    TOKEN = 'token'
    REMOVED = 'removed'
    HISTORICAL = 'historical'
    NON_HISTORICAL = 'nonHistorical'
    USED = 'used'
    IN_HANGAR = 'inHangar'
    NOT_IN_HANGAR = 'notInHangar'
    IS_HAS_CREW = 'hasCrew'
    FAVOURITE = 'favorite'
    DOCUMENTS = 'documents'
    SKINS = 'skins'


TOGGLE_FILTER_ICONS_MAP = {ToggleFilters.IN_BARRACKS: R.images.gui.maps.icons.filters.barracks_check(),
 ToggleFilters.ON_VEHICLE: R.images.gui.maps.icons.filters.vehicle_check(),
 ToggleFilters.DISMISSED: R.images.gui.maps.icons.filters.dismissed(),
 ToggleFilters.CREW: R.images.gui.maps.icons.filters.crew_check(),
 ToggleFilters.REMOVED: R.images.gui.maps.icons.filters.time(),
 ToggleFilters.HISTORICAL: R.images.gui.maps.icons.filters.historical(),
 ToggleFilters.NON_HISTORICAL: R.images.gui.maps.icons.filters.non_historical(),
 ToggleFilters.USED: R.images.gui.maps.icons.filters.crew_check(),
 ToggleFilters.IN_HANGAR: R.images.gui.maps.icons.filters.barracks_check(),
 ToggleFilters.NOT_IN_HANGAR: R.images.gui.maps.icons.filters.out_of_barracks(),
 ToggleFilters.IS_HAS_CREW: R.images.gui.maps.icons.filters.crew_check(),
 ToggleFilters.FAVOURITE: R.images.gui.maps.icons.filters.favourite(),
 ToggleFilters.TOKEN: R.invalid(),
 ToggleFilters.DOCUMENTS: R.images.gui.maps.icons.filters.docs(),
 ToggleFilters.SKINS: R.images.gui.maps.icons.filters.skins()}
