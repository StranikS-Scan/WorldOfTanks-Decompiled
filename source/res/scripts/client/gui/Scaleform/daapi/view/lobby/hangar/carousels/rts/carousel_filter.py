# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/rts/carousel_filter.py
from account_helpers.AccountSettings import RTS_CAROUSEL_FILTER_1, RTS_CAROUSEL_FILTER_2, RTS_CAROUSEL_FILTER_CLIENT_1
from gui.rts_battles.rts_constants import RTS_CAROUSEL_FILTER_KEY
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CarouselFilter, EventCriteriesGroup, BasicCriteriesGroup

class RTSCarouselFilter(CarouselFilter):

    def __init__(self):
        super(RTSCarouselFilter, self).__init__()
        self._serverSections = (RTS_CAROUSEL_FILTER_1, RTS_CAROUSEL_FILTER_2)
        self._clientSections = (RTS_CAROUSEL_FILTER_CLIENT_1,)

    def _setCriteriaGroups(self):
        self._criteriesGroups = (EventCriteriesGroup(), RTSCriteriesGroup())


class RTSCriteriesGroup(BasicCriteriesGroup):

    def update(self, filters):
        super(RTSCriteriesGroup, self).update(filters)
        if filters[RTS_CAROUSEL_FILTER_KEY]:
            self._criteria |= ~REQ_CRITERIA.VEHICLE.HAS_CUSTOM_STATE(Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE)
