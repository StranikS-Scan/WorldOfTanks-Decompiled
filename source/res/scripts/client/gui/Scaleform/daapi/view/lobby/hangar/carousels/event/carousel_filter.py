# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/event/carousel_filter.py
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import CarouselFilter

class EventCarouselFilter(CarouselFilter):

    def __init__(self):
        super(EventCarouselFilter, self).__init__()
        self._serverSections = ()
        self._clientSections = ()
        self._criteriesGroups = ()
