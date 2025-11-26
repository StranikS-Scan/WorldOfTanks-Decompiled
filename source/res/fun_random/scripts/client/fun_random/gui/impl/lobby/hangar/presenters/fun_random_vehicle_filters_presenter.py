# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/presenters/fun_random_vehicle_filters_presenter.py
from __future__ import absolute_import
from gui.impl.lobby.hangar.presenters.vehicle_filters_presenter import VehicleFiltersDataProvider

class FunRandomVehicleFiltersDataProvider(VehicleFiltersDataProvider):

    @classmethod
    def _getBaseSpecialSection(cls):
        return super(FunRandomVehicleFiltersDataProvider, cls)._getBaseSpecialSection() + ['funRandom']
