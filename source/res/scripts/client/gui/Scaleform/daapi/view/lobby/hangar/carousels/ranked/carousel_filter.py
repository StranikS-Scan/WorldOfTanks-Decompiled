# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/ranked/carousel_filter.py
import logging
import constants
from account_helpers.AccountSettings import RANKED_CAROUSEL_FILTER_1, RANKED_CAROUSEL_FILTER_2, RANKED_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import EventCriteriesGroup
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME, VEHICLE_ACTION_GROUPS_LABELS
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass.carousel_filter import BattlePassCriteriesGroup, BattlePassCarouselFilter
_logger = logging.getLogger(__name__)
_NOT_DEFINED = constants.ACTIONS_GROUP_TYPE_TO_LABEL[constants.ACTIONS_GROUP_TYPE.NOT_DEFINED]

class RankedCarouselFilter(BattlePassCarouselFilter):

    def __init__(self):
        super(RankedCarouselFilter, self).__init__()
        self._serverSections = (RANKED_CAROUSEL_FILTER_1, RANKED_CAROUSEL_FILTER_2, BATTLEPASS_CAROUSEL_FILTER_1)
        self._clientSections = (RANKED_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1)
        self._criteriesGroups = (EventCriteriesGroup(), RankedCriteriesGroup())

    def switch(self, key, save=True):
        updateDict = {key: not self._filters[key]}
        if key in VEHICLE_CLASS_NAME.ALL() and len(self.__getCurrentVehicleClasses(updateDict)) != 1:
            updateDict.update(self.__resetRoles())
        if updateDict:
            self.update(updateDict, save)

    def __getCurrentVehicleClasses(self, updateDict):
        return {vehClass for vehClass in VEHICLE_CLASS_NAME.ALL() if (self._filters[vehClass] or updateDict.get(vehClass)) and updateDict.get(vehClass) is not False}

    @staticmethod
    def __resetRoles():
        return {role:False for role in VEHICLE_ACTION_GROUPS_LABELS}


class RankedCriteriesGroup(BattlePassCriteriesGroup):

    def update(self, filters):
        super(RankedCriteriesGroup, self).update(filters)
        actionsGroups = []
        if not filters[_NOT_DEFINED]:
            for actionsGroup in VEHICLE_ACTION_GROUPS_LABELS:
                if filters[actionsGroup]:
                    actionsGroups.append(actionsGroup)

        if actionsGroups:
            self._criteria |= REQ_CRITERIA.VEHICLE.ACTION_GROUPS(actionsGroups)
