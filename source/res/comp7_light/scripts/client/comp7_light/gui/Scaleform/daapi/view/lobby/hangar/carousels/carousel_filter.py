# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/lobby/hangar/carousels/carousel_filter.py
from account_helpers.AccountSettings import COMP7_LIGHT_CAROUSEL_FILTER_1, COMP7_LIGHT_CAROUSEL_FILTER_2, COMP7_LIGHT_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1, COMP7_LIGHT_CAROUSEL_FILTER_3
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass.carousel_filter import BattlePassCarouselFilter, BattlePassCriteriesGroup
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import EventCriteriesGroup
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightCarouselFilter(BattlePassCarouselFilter):

    def __init__(self):
        super(Comp7LightCarouselFilter, self).__init__()
        self._serverSections = (COMP7_LIGHT_CAROUSEL_FILTER_1,
         COMP7_LIGHT_CAROUSEL_FILTER_2,
         BATTLEPASS_CAROUSEL_FILTER_1,
         COMP7_LIGHT_CAROUSEL_FILTER_3)
        self._clientSections = (COMP7_LIGHT_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1)
        self._criteriesGroups = (EventCriteriesGroup(), Comp7LightCriteriesGroup())


class Comp7LightCriteriesGroup(BattlePassCriteriesGroup):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def update(self, filters):
        super(Comp7LightCriteriesGroup, self).update(filters)
        if filters.get('comp7'):
            self._criteria |= REQ_CRITERIA.CUSTOM(self._comp7LightCriteria)

    @classmethod
    def _comp7LightCriteria(cls, vehicle):
        return cls.__comp7LightController.isSuitableVehicle(vehicle) is None
