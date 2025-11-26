# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/lobby/hangar/presenters/comp7_core_vehicle_filters_presenter.py
import typing
from gui.filters.carousel_filter import FILTER_KEYS
from gui.impl.lobby.hangar.presenters.vehicle_filters_presenter import VehicleFiltersDataProvider
if typing.TYPE_CHECKING:
    from typing import List

class Comp7CoreVehicleFiltersDataProvider(VehicleFiltersDataProvider):

    @classmethod
    def _getBaseSpecialSection(cls):
        specialSection = super(Comp7CoreVehicleFiltersDataProvider, cls)._getBaseSpecialSection()
        specialSection.append(FILTER_KEYS.EVENT)
        return specialSection
