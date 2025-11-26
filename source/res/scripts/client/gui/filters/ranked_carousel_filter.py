# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/filters/ranked_carousel_filter.py
import logging
from account_helpers.AccountSettings import RANKED_CAROUSEL_FILTER_1, RANKED_CAROUSEL_FILTER_2, RANKED_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1, RANKED_CAROUSEL_FILTER_3
from gui.filters.battle_pass_carousel_filter import BattlePassCarouselFilter, BattlePassCriteriesGroup
from gui.filters.carousel_filter import EventCriteriesGroup
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
_logger = logging.getLogger(__name__)

class RankedCarouselFilter(BattlePassCarouselFilter):

    def __init__(self):
        super(RankedCarouselFilter, self).__init__()
        self._serverSections = (RANKED_CAROUSEL_FILTER_1,
         RANKED_CAROUSEL_FILTER_2,
         BATTLEPASS_CAROUSEL_FILTER_1,
         RANKED_CAROUSEL_FILTER_3)
        self._clientSections = (RANKED_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1)
        self._criteriesGroups = (EventCriteriesGroup(), RankedCriteriesGroup())


class RankedCriteriesGroup(BattlePassCriteriesGroup):
    __rankedBattlesController = dependency.descriptor(IRankedBattlesController)

    def update(self, filters):
        super(RankedCriteriesGroup, self).update(filters)
        if filters.get('ranked'):
            self._criteria |= REQ_CRITERIA.CUSTOM(self._rankedCriteria)

    @classmethod
    def _rankedCriteria(cls, vehicle):
        return cls.__rankedBattlesController.isSuitableVehicle(vehicle) is None
