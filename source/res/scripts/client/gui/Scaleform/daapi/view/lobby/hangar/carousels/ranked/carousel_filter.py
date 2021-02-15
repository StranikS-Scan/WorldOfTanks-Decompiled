# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/ranked/carousel_filter.py
import logging
import constants
from account_helpers.AccountSettings import RANKED_CAROUSEL_FILTER_1, RANKED_CAROUSEL_FILTER_2, RANKED_CAROUSEL_FILTER_CLIENT_1, BATTLEPASS_CAROUSEL_FILTER_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import EventCriteriesGroup
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME, VEHICLE_ACTION_GROUPS_LABELS_BY_CLASS, VEHICLE_ACTION_GROUPS_LABELS
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
        if key in VEHICLE_CLASS_NAME.ALL():
            updateDict = self.__switchRoleFiltersByVehicleClass(updateDict, key)
        elif key in VEHICLE_ACTION_GROUPS_LABELS:
            updateDict = self.__switchRoleFiltersByKey(updateDict, key)
        if updateDict:
            self.update(updateDict, save)

    def __getCurrentVehicleClasses(self):
        return {vehClass for vehClass in VEHICLE_CLASS_NAME.ALL() if self._filters[vehClass]}

    def __getCurrentRole(self):
        for role in VEHICLE_ACTION_GROUPS_LABELS:
            if self._filters[role]:
                return role

        _logger.error('There is no selected role in RankedCarouselFilter. Forced AnyRole on.')
        self.update({_NOT_DEFINED: True}, True)
        return _NOT_DEFINED

    def __getFirstClassAvailableRole(self, key):
        currentClasses = self.__getCurrentVehicleClasses()
        if self._filters[key]:
            currentClasses.discard(key)
            currentClasses = currentClasses or set(VEHICLE_CLASS_NAME.ALL())
        else:
            currentClasses.add(key)
        availableRoles = set()
        for vehClass in currentClasses:
            availableRoles.update(VEHICLE_ACTION_GROUPS_LABELS_BY_CLASS[vehClass])

        for role in VEHICLE_ACTION_GROUPS_LABELS:
            if role in availableRoles:
                return role

        _logger.error('There is no available role in current vehicle classes. Forced AnyRole on.')
        return _NOT_DEFINED

    def __switchRoleFiltersByKey(self, updateDict, key):
        currentRole = self.__getCurrentRole()
        if key == currentRole:
            return {}
        updateDict.update({key: True,
         currentRole: False})
        return updateDict

    def __switchRoleFiltersByVehicleClass(self, updateDict, key):
        firstAvailableRole = self.__getFirstClassAvailableRole(key)
        currentRole = self.__getCurrentRole()
        if firstAvailableRole != currentRole:
            updateDict.update({firstAvailableRole: True,
             currentRole: False})
        return updateDict


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
