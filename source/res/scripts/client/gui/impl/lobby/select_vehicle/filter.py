# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/select_vehicle/filter.py
from __future__ import absolute_import
from account_helpers.AccountSettings import SELECT_VEHICLES_CAROUSEL_FILTER_1
from gui.filters.carousel_filter import BasicCriteriesGroup, CriteriesGroup, SessionCarouselFilter

class SelectVehiclesCriteriaGroup(BasicCriteriesGroup):

    def update(self, filters):
        CriteriesGroup.update(self, filters)
        self._setNationsCriteria(filters)
        self._setClassesCriteria(filters)
        self._setLevelsCriteria(filters)
        self._setEliteAndPremiumCriteria(filters)
        self._setFavoriteVehicleCriteria(filters)
        self._setVehicleNameCriteria(filters)


class SelectVehiclesCarouselFilter(SessionCarouselFilter):

    def __init__(self):
        super(SelectVehiclesCarouselFilter, self).__init__()
        self._clientSections = (SELECT_VEHICLES_CAROUSEL_FILTER_1,)
        self._criteriesGroups = (SelectVehiclesCriteriaGroup(),)
