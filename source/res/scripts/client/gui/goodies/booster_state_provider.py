# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/booster_state_provider.py
import typing
import logging
import BigWorld
from Event import Event
from gui.goodies.goodie_items import Booster
from gui.shared.money import Money
from goodies.goodie_constants import GOODIE_STATE, GOODIE_VARIETY, GOODIE_TARGET_TYPE, PR2BoosterIDs
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.requesters.GoodiesRequester import GoodieVariable
from gui.shared.utils.requesters.ShopRequester import _NamedGoodieData
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers.time_utils import getServerTimeDiffInLocal
from skeletons.gui.goodies import IBoostersStateProvider
if typing.TYPE_CHECKING:
    from typing import Dict, Any, Optional, List, Tuple, Union
    from gui.shared.utils.requesters.ShopRequester import _ResourceData
    from goodies.goodie_constants import GOODIE_RESOURCE_TYPE
_logger = logging.getLogger(__name__)

class BoosterStateProvider(IBoostersStateProvider):

    def __init__(self):
        super(BoosterStateProvider, self).__init__()
        self.__personalGoodies = None
        self.__activeResources = None
        self.__boosters = None
        self.__activeBoosterTypes = None
        self.__notificationManager = Notifiable()
        self.onStateUpdated = Event()
        return

    @property
    def personalGoodies(self):
        return self.__personalGoodies

    def onAvatarBecomePlayer(self):
        BigWorld.player().onGoodiesSnapshotUpdated += self.buildCache
        self.buildCache()
        self.__notificationManager.addNotificator(SimpleNotifier(self._timeTillNextNotification, self.buildCache))
        self.__notificationManager.startNotification()

    def onAvatarBecomeNonPlayer(self):
        BigWorld.player().onGoodiesSnapshotUpdated -= self.buildCache
        self.clear()

    def fini(self):
        player = BigWorld.player()
        if hasattr(player, 'goodiesSnapshot'):
            player.onGoodiesSnapshotUpdated -= self.buildCache
        self.onStateUpdated.clear()
        self.clear()

    def clear(self):
        self.__personalGoodies = None
        self.__activeResources = None
        self.__activeBoosterTypes = None
        self.__boosters = None
        self.__notificationManager.clearNotification()
        return

    def getBoosters(self, criteria=None):
        results = {}
        if self.__boosters is None:
            return results
        else:
            for goodieID, booster in self.__boosters.iteritems():
                if criteria(booster):
                    results[goodieID] = booster

            return results

    def getBooster(self, boosterId):
        return self.__boosters[boosterId] if self.__boosters is not None and boosterId in self.__boosters else None

    def getClanReserves(self):
        return dict()

    def getActiveResources(self):
        return [] if self.__activeResources is None else self.__activeResources

    def getActiveBoosterTypes(self):
        return [] if self.__activeBoosterTypes is None else self.__activeBoosterTypes

    def isBoosterHiddenInShop(self, boosterID):
        return False

    def haveBooster(self, boosterID):
        return boosterID in self.__boosters

    def addBooster(self, bID, booster, stateInfo, resourceData):
        self.__boosters[bID] = booster
        state = stateInfo['state']
        expirations, count = self._filterOutExpired(stateInfo)
        self.__personalGoodies[bID] = GoodieVariable(state, stateInfo['finishTime'], count, expirations)
        if state == GOODIE_STATE.ACTIVE:
            self.__activeBoosterTypes.add(resourceData.resourceType)
            self.__activeResources.add(resourceData)

    def getBoosterPriceData(self, boosterID):
        defMoney = Money()
        return (defMoney,
         defMoney,
         defMoney,
         defMoney)

    def buildCache(self):
        self.__personalGoodies = {}
        self.__activeResources = set()
        self.__boosters = {}
        self.__activeBoosterTypes = set()
        goodiesSnapshot = BigWorld.player().goodiesSnapshot
        if goodiesSnapshot:
            for snapshot in goodiesSnapshot:
                bId = snapshot['goodieID']
                resource = snapshot['resource']
                descr = _NamedGoodieData(GOODIE_VARIETY.BOOSTER, (GOODIE_TARGET_TYPE.ON_POST_BATTLE, None, 0), True, snapshot['lifetime'], snapshot['useby'], 0, False, None, (resource['type'], resource['value'], resource['isPercentage']), bId in PR2BoosterIDs.ALL_EXPIRABLE_ITEMS, True)
                booster = Booster(bId, descr, self)
                self.addBooster(bId, booster, snapshot['stateInfo'], descr.resource)
                _logger.debug('[BoosterStateProvider] %d: %s', bId, booster)

            self.onStateUpdated()
        return

    def _filterOutExpired(self, stateInfo):
        if not stateInfo['expirations']:
            return (stateInfo['expirations'], stateInfo['count'])
        valid = {}
        expired = {}
        newCount = stateInfo['count']
        for timestamp, count in stateInfo['expirations'].iteritems():
            if getServerTimeDiffInLocal(timestamp):
                valid[timestamp] = count
            expired[timestamp] = count
            newCount -= count

        if stateInfo['state'] == GOODIE_STATE.ACTIVE and expired:
            nearest = min(expired.iterkeys())
            valid[nearest] = 1
            newCount += 1
        return (valid, newCount)

    def _timeTillNextNotification(self):
        from gui.impl.lobby.personal_reserves.personal_reserves_utils import findNearestExpiryTimeInBoostersList
        boosters = self.getBoosters(REQ_CRITERIA.BOOSTER.ENABLED)
        nextExpiry = findNearestExpiryTimeInBoostersList(boosters.values())
        timeLeft = getServerTimeDiffInLocal(nextExpiry)
        return timeLeft
