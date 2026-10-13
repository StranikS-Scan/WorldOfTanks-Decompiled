# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/filters/fort_rush_carousel_filter.py
from __future__ import absolute_import
from account_helpers.AccountSettings import FORT_RUSH_CAROUSEL_FILTER_1
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from gui.filters.carousel_filter import CustomizationCriteriesGroup, FILTER_KEYS, SessionCarouselFilter
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency

class FortRushCriteriesGroup(CustomizationCriteriesGroup):
    __battleController = dependency.descriptor(IFortRushBattleController)

    def update(self, filters):
        super(FortRushCriteriesGroup, self).update(filters)
        if filters.get(FILTER_KEYS.EVENT):
            self._criteria |= REQ_CRITERIA.INVENTORY | REQ_CRITERIA.CUSTOM(self.__isSuitableVehicle)

    @classmethod
    def __isSuitableVehicle(cls, vehicle):
        return cls.__battleController.isSuitableVehicle(vehicle) is None


class FortRushCarouselFilter(SessionCarouselFilter):

    def __init__(self):
        super(FortRushCarouselFilter, self).__init__()
        self._clientSections = (FORT_RUSH_CAROUSEL_FILTER_1,)
        self._setCriteriaGroups()

    def _setCriteriaGroups(self):
        self._criteriesGroups = (FortRushCriteriesGroup(),)
