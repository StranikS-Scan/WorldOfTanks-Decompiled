# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/battle_carousel_filters.py
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import RoleCriteriesGroup
from gui.shared.utils.requesters.ItemsRequester import RequestCriteria, PredicateCondition
FL_RENT = RequestCriteria(PredicateCondition(lambda item: item.name.endswith('_FL')))

class FLRentedCriteriesGroup(RoleCriteriesGroup):

    def update(self, filters):
        super(FLRentedCriteriesGroup, self).update(filters)
        if not filters['rented']:
            self._criteria |= ~FL_RENT

    @staticmethod
    def isApplicableFor(vehicle):
        return True
