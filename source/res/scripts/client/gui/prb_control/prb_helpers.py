# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/prb_helpers.py
import logging
import typing
from future.utils import viewvalues
from gui.shared.badges import buildBadge
from gui.shared.gui_items.badge import BadgeLayouts
from gui.shared.system_factory import collectModeNameKwargsByPrbType, collectModeNameKwargsByQueueType
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IPlatoonController
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from gui.impl.lobby.platoon.platoon_config import PREBATTLE_TYPE_TO_VEH_CRITERIA
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _findFirstPrefixBadge(selectedBadges, itemsCache=None):
    badgeDescrs = itemsCache.items.badges.available
    if not isinstance(selectedBadges, (tuple, list)):
        if isinstance(selectedBadges, int):
            return selectedBadges
        return 0
    for sbID in selectedBadges:
        badgeDescr = badgeDescrs.get(sbID)
        if badgeDescr and badgeDescr['layout'] == BadgeLayouts.PREFIX:
            return sbID


class BadgesHelper(object):

    def __init__(self, badges=None):
        if isinstance(badges, (list, tuple)) and badges and not isinstance(badges[0], (list, tuple)):
            _logger.error('Converting badges data %s', badges)
            self.__badgesRawData = (badges, [])
        else:
            self.__badgesRawData = badges or ([], [])
        self.__badges = {}
        self.__prefixBadgeID = None
        return

    def getBadge(self):
        badgeID = self.__getBadgeID()
        if badgeID <= 0:
            return None
        else:
            if badgeID not in self.__badges:
                self.__badges[badgeID] = buildBadge(badgeID, self.__getBadgeExtraInfo())
            return self.__badges[badgeID]

    def __getBadgeID(self):
        if self.__prefixBadgeID is None:
            self.__prefixBadgeID = _findFirstPrefixBadge(self.__getSelectedBadges())
        return self.__prefixBadgeID

    def __getSelectedBadges(self):
        if not self.__badgesRawData:
            _logger.error('Invalid selected badge data')
            return []
        return self.__badgesRawData[0]

    def __getBadgeExtraInfo(self):
        if len(self.__badgesRawData) < 2:
            _logger.error('Invalid badge data %s', self.__badgesRawData)
            return None
        else:
            return self.__badgesRawData[1]


def getModeNameKwargs(entityType, isQueue=True):
    collector = collectModeNameKwargsByQueueType if isQueue else collectModeNameKwargsByPrbType
    return collector(entityType) or {}


class IVehicleAutoSearchHelper(object):

    @classmethod
    def getVehiclesLevelsChecker(cls):
        raise NotImplementedError


class DefaultVehicleAutoSearchHelper(IVehicleAutoSearchHelper):
    platoonCtrl = dependency.descriptor(IPlatoonController)
    itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def getVehiclesLevelsChecker(cls):
        prebattleType = cls.platoonCtrl.getPrbEntityType()
        allowedLevels = cls.platoonCtrl.getAllowedTankLevels(prebattleType)
        vehLevels = set()
        criteria = REQ_CRITERIA.INVENTORY
        criteria |= ~REQ_CRITERIA.VEHICLE.DISABLED_IN_PREM_IGR
        criteria |= PREBATTLE_TYPE_TO_VEH_CRITERIA.get(prebattleType, REQ_CRITERIA.EMPTY)
        allowedList = [ lvl for lvl in range(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1) if allowedLevels & 1 << lvl ]
        criteria |= REQ_CRITERIA.VEHICLE.LEVELS(allowedList)
        vehicles = cls.itemsCache.items.getVehicles(criteria)
        for v in viewvalues(vehicles):
            state, vStateLvl = v.getState()
            if state in (Vehicle.VEHICLE_STATE.LOCKED, Vehicle.VEHICLE_STATE.IN_PREBATTLE) and v.checkUndamagedState(Vehicle.VEHICLE_STATE.UNDAMAGED) == Vehicle.VEHICLE_STATE.UNDAMAGED or vStateLvl not in (Vehicle.VEHICLE_STATE_LEVEL.CRITICAL,
             Vehicle.VEHICLE_STATE_LEVEL.WARNING,
             Vehicle.VEHICLE_STATE_LEVEL.RENTABLE,
             Vehicle.VEHICLE_STATE_LEVEL.ATTENTION):
                vehLevels.add(v.level)

        return vehLevels
