# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/lobby/hangar/carousel/carousel_filter.py
import logging
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CarouselFilter, RoleCriteriesGroup
from gui.shared.utils.requesters import REQ_CRITERIA
from account_helpers.AccountSettings import HW22_CAROUSEL_FILTER_1, HW22_CAROUSEL_FILTER_2, HW22_CAROUSEL_FILTER_CLIENT_1
_logger = logging.getLogger(__name__)
EVENT_VEHICLES_FILTER = 'event'
_ACCEPTABLE_LEVELS = [6, 7, 8]

class HW22CarouselFilter(CarouselFilter):

    def __init__(self):
        super(HW22CarouselFilter, self).__init__()
        self._serverSections = (HW22_CAROUSEL_FILTER_1, HW22_CAROUSEL_FILTER_2)
        self._clientSections = (HW22_CAROUSEL_FILTER_CLIENT_1,)

    def _setCriteriaGroups(self):
        self._criteriesGroups = (HW22CriteriesGroup(),)


class HW22CriteriesGroup(RoleCriteriesGroup):

    def update(self, filters):
        super(HW22CriteriesGroup, self).update(filters)
        if filters.get(EVENT_VEHICLES_FILTER):
            self._criteria |= REQ_CRITERIA.VEHICLE.LEVELS(_ACCEPTABLE_LEVELS)
