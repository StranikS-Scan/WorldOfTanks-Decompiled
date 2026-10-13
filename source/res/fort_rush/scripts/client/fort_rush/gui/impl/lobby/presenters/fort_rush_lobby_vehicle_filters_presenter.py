# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/presenters/fort_rush_lobby_vehicle_filters_presenter.py
from __future__ import absolute_import
from typing import List
from gui.filters.carousel_filter import FILTER_KEYS
from gui.impl.lobby.hangar.presenters.vehicle_filters_presenter import VehicleFiltersDataProvider
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
_VEHICLE_TYPES_ORDER = (VEHICLE_CLASS_NAME.LIGHT_TANK,
 VEHICLE_CLASS_NAME.MEDIUM_TANK,
 VEHICLE_CLASS_NAME.HEAVY_TANK,
 VEHICLE_CLASS_NAME.AT_SPG)

class FortRushLobbyVehicleFiltersPresenter(VehicleFiltersDataProvider):

    @classmethod
    def _getVehicleTypesFilter(cls):
        return _VEHICLE_TYPES_ORDER

    @classmethod
    def _getBaseSpecialSection(cls):
        return [FILTER_KEYS.EVENT,
         FILTER_KEYS.FAVORITE,
         FILTER_KEYS.RENTED,
         FILTER_KEYS.ELITE,
         FILTER_KEYS.PREMIUM,
         FILTER_KEYS.OWN_3D_STYLE,
         FILTER_KEYS.CAN_INSTALL_ATTACHMENTS]
