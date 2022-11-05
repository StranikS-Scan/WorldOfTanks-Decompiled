# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/hangar/carousel/carousel_filter.py
from account_helpers.AccountSettings import BATTLEPASS_CAROUSEL_FILTER_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1, FUN_RANDOM_CAROUSEL_FILTER_1, FUN_RANDOM_CAROUSEL_FILTER_2, FUN_RANDOM_CAROUSEL_FILTER_CLIENT_1
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import EventCriteriesGroup
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass.carousel_filter import BattlePassCarouselFilter, BattlePassCriteriesGroup
from gui.shared.utils.requesters import REQ_CRITERIA

class FunRandomCarouselFilter(BattlePassCarouselFilter):

    def __init__(self):
        super(FunRandomCarouselFilter, self).__init__()
        self._serverSections = (FUN_RANDOM_CAROUSEL_FILTER_1, FUN_RANDOM_CAROUSEL_FILTER_2, BATTLEPASS_CAROUSEL_FILTER_1)
        self._clientSections = (FUN_RANDOM_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1)
        self._criteriesGroups = (EventCriteriesGroup(), FunRandomCriteriesGroup())


class FunRandomCriteriesGroup(BattlePassCriteriesGroup, FunSubModesWatcher):

    def update(self, filters):
        super(FunRandomCriteriesGroup, self).update(filters)
        self.__addFunRandomCriteria(filters)

    @hasDesiredSubMode()
    def __addFunRandomCriteria(self, filters):
        if filters.get('funRandom'):
            self._criteria |= ~REQ_CRITERIA.CUSTOM(self.getDesiredSubMode().isSuitableVehicle)
