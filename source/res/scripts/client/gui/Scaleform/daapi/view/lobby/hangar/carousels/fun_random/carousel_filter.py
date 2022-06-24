# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/fun_random/carousel_filter.py
from account_helpers.AccountSettings import BATTLEPASS_CAROUSEL_FILTER_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1, FUN_RANDOM_CAROUSEL_FILTER_1, FUN_RANDOM_CAROUSEL_FILTER_2, FUN_RANDOM_CAROUSEL_FILTER_CLIENT_1
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import EventCriteriesGroup
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass.carousel_filter import BattlePassCarouselFilter, BattlePassCriteriesGroup
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

class FunRandomCarouselFilter(BattlePassCarouselFilter):

    def __init__(self):
        super(FunRandomCarouselFilter, self).__init__()
        self._serverSections = (FUN_RANDOM_CAROUSEL_FILTER_1, FUN_RANDOM_CAROUSEL_FILTER_2, BATTLEPASS_CAROUSEL_FILTER_1)
        self._clientSections = (FUN_RANDOM_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1)
        self._criteriesGroups = (EventCriteriesGroup(), FunRandomCriteriesGroup())


class FunRandomCriteriesGroup(BattlePassCriteriesGroup):
    __controller = dependency.descriptor(IFunRandomController)

    def update(self, filters):
        super(FunRandomCriteriesGroup, self).update(filters)
        if filters.get('funRandom'):
            self._criteria |= ~REQ_CRITERIA.CUSTOM(self.__controller.isSuitableVehicle)
