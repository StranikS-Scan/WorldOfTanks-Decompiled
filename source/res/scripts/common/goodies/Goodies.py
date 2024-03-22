# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/Goodies.py
import collections
from typing import TYPE_CHECKING
from WeakMethod import WeakMethod
from debug_utils import LOG_WARNING, LOG_DEBUG_DEV
from goodie_constants import GOODIE_STATE, MAX_ACTIVE_BOOSTERS, ACTION_REASON_ID
from soft_exception import SoftException
from GoodieResources import GoodieResource
from GoodieTargets import GoodieTarget
from Goodie import decrementExpirationsInOrder, mergeExpirationsInto
if TYPE_CHECKING:
    from goodies.GoodieConditions import GoodieConditionType
    from goodies.GoodieTargets import GoodieTargetType
    from goodies.GoodieResources import GoodieResourceType
    from goodies.GoodieValue import GoodieValueType
    from typing import Type, Dict, Optional, Callable, Union, Tuple, Set, Iterator, List
    from goodies.Goodie import Goodie
    from goodies.GoodieDefinition import GoodieDefinition
    UpdateCallback = Callable[[Goodie, int, int], None]
    RemoveCallback = Callable[[int, int, int], None]

class GoodieException(SoftException):
    pass


class _ActualGoodiesDict(collections.MutableMapping, dict):

    def __init__(self, definedGoodiesDict, resourceIndexDict):
        self._definedGoodiesDict = definedGoodiesDict
        self._resourceIndexDict = resourceIndexDict
        super(_ActualGoodiesDict, self).__init__()

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        resource = self._definedGoodiesDict[key].resource
        if value.isActive():
            self._resourceIndexDict[resource] = key
        else:
            goodieID = self._resourceIndexDict.get(resource, None)
            if goodieID == key:
                self._resourceIndexDict.pop(resource, None)
        dict.__setitem__(self, key, value)
        return

    def __delitem__(self, key):
        resource = self._definedGoodiesDict[key].resource
        goodieID = self._resourceIndexDict.get(resource, None)
        if goodieID == key:
            self._resourceIndexDict.pop(resource, None)
        dict.__delitem__(self, key)
        return

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)

    def __contains__(self, x):
        return dict.__contains__(self, x)

    def __getResource(self, goodieID):
        goodie = dict.__getitem__(self, goodieID)
        if goodie is None:
            return
        else:
            defined = self._definedGoodiesDict.get(goodieID, None)
            return None if defined is None else (defined.resource, defined.value)

    def checkResource(self, goodieID):
        resourceTuple = self.__getResource(goodieID)
        if resourceTuple is None:
            return
        else:
            resource, value = resourceTuple
            anotherGoodieID = self._resourceIndexDict.get(resource)
            return anotherGoodieID if anotherGoodieID is not None else None

    def compareByResource(self, goodieID, anotherGoodieID):
        resourceTuple = self.__getResource(goodieID)
        anotherResourceTuple = self.__getResource(anotherGoodieID)
        if resourceTuple is None or anotherResourceTuple is None:
            return False
        resource, value = resourceTuple
        anotherResource, anotherValue = anotherResourceTuple
        if anotherResource != resource:
            return False
        else:
            return True if anotherValue > value else False


class Goodies(object):

    def __init__(self, definedGoodies, updateCallback=None, removeCallback=None):
        self.definedGoodies = definedGoodies
        self.__resourceIndex = {}
        self.actualGoodies = _ActualGoodiesDict(self.definedGoodies, self.__resourceIndex)
        if updateCallback:
            self._updateCallback = WeakMethod(updateCallback)
        else:
            self._updateCallback = None
        if removeCallback:
            self._removeCallback = WeakMethod(removeCallback)
        else:
            self._removeCallback = None
        return

    def __updateCallback(self, goodie, reasonID, amountDelta):
        if self._updateCallback is not None:
            callbackRef = self._updateCallback()
            if callbackRef:
                callbackRef(goodie, reasonID, amountDelta)
        return

    def __removeCallback(self, goodieID, reasonID, amountDelta):
        if self._removeCallback is not None:
            callbackRef = self._removeCallback()
            if callbackRef:
                callbackRef(goodieID, reasonID, amountDelta)
        return

    def __append(self, goodieDefinition, reasonID, state=None, finishTime=None, counter=None, expirations=None):
        goodie = goodieDefinition.createGoodie(state, finishTime, counter, expirations)
        if goodie is None:
            return
        else:
            self.actualGoodies[goodieDefinition.uid] = goodie
            self.__updateCallback(goodie, reasonID, goodie.counter)
            return

    def __expire(self, goodieID):
        LOG_DEBUG_DEV('[GOODIE] __expire goodie {} '.format(goodieID))
        goodieDefinition = self.definedGoodies.get(goodieID, None)
        if goodieDefinition is None:
            return
        else:
            goodie = self.actualGoodies.get(goodieID, None)
            if goodie is None:
                return
            if not goodieDefinition.isExpirable():
                return
            expiredTimestamps, newExpirations = goodie.splitExpirations()
            if not expiredTimestamps:
                return
            if goodie.isActive():
                closestExpiration = min(expiredTimestamps.iterkeys())
                newExpirations[closestExpiration] = 1
            newCounter = sum(newExpirations.itervalues())
            if newCounter == goodie.counter:
                return
            if newCounter <= 0:
                self.__erase(goodieID, ACTION_REASON_ID.EXPIRATION_HAS_PASSED)
            else:
                self.__updateActual(goodieDefinition, newState=goodie.state, newFinishTime=goodie.finishTime, newCounter=newCounter, newExpirations=newExpirations, reasonID=ACTION_REASON_ID.EXPIRATION_HAS_PASSED)
            return

    def __erase(self, goodieID, reasonID):
        LOG_DEBUG_DEV('[GOODIE] __erase goodie {}, reason id {} '.format(goodieID, reasonID))
        goodie = self.actualGoodies.get(goodieID, None)
        if goodie is None:
            return
        else:
            goodieAmount = goodie.counter
            del self.actualGoodies[goodieID]
            self.__removeCallback(goodieID, reasonID, -goodieAmount)
            return

    def __updateActual(self, goodieDefinition, newState, newFinishTime, newCounter, newExpirations, reasonID):
        goodie = goodieDefinition.createGoodie(state=newState, finishTime=newFinishTime, counter=newCounter, expirations=newExpirations)
        if goodie is None:
            return
        else:
            amountDelta = newCounter
            prevGoodie = self.actualGoodies.get(goodieDefinition.uid, None)
            if prevGoodie is not None:
                amountDelta -= prevGoodie.counter
            self.actualGoodies[goodieDefinition.uid] = goodie
            self.__updateCallback(goodie, reasonID, amountDelta)
            return

    def __decrement(self, goodieID, amount, reasonID, skipActive):
        LOG_DEBUG_DEV('[GOODIE] __decrement goodie {}, amount {}, reason id {} '.format(goodieID, amount, reasonID))
        goodieDefinition = self.definedGoodies.get(goodieID, None)
        if goodieDefinition is None:
            return
        else:
            goodie = self.actualGoodies.get(goodieID, None)
            if goodie is None:
                return
            if skipActive and goodieDefinition.isActivatable() and goodie.isActive() and not goodie.isEffectFinished():
                return
            newCounter = goodie.counter - amount
            if newCounter <= 0:
                self.__erase(goodieID, reasonID)
            else:
                newExpirations = decrementExpirationsInOrder(amount, goodie.expirations)
                self.__updateActual(goodieDefinition, newState=None, newFinishTime=None, newCounter=newCounter, newExpirations=newExpirations, reasonID=reasonID)
            return

    def __checkDuplicateResources(self, allResourcesByType, affectedResource):
        if affectedResource.__class__ in allResourcesByType:
            return True
        allResourcesByType.add(affectedResource.__class__)
        return False

    def __show(self, target, resources, returnDeltas, applyToZero):
        if not isinstance(resources, set):
            resources = {resources}
        toUpdate = {}
        for resource in resources:
            bestGoodieDef, bestDeltaValue = self.__getBestAvailableGoodie(target, resource, applyToZero)
            if bestGoodieDef is not None:
                if returnDeltas:
                    toUpdate[bestGoodieDef.uid] = bestDeltaValue
                else:
                    toUpdate[bestGoodieDef.uid] = bestGoodieDef.apply(resources, applyToZero)

        return toUpdate

    def actual(self):
        return self.actualGoodies.itervalues()

    def actualIds(self):
        return set(self.actualGoodies.iterkeys())

    def __getBestAvailableGoodie(self, target, resource, applyToZero):
        bestGoodieDef, bestDelta = (None, None)
        for goodie in self.actualGoodies.itervalues():
            goodieDefinition = self.definedGoodies[goodie.uid]
            if goodieDefinition.isActivatable() and not goodie.isActive():
                continue
            if issubclass(target.__class__, goodieDefinition.target.__class__) and target._targetID == goodieDefinition.target._targetID and goodieDefinition.resource == resource.__class__:
                delta = goodieDefinition.apply_delta(resource, applyToZero)
                if delta is not None and (bestGoodieDef is None or bestDelta.value < delta.value):
                    bestGoodieDef, bestDelta = goodieDefinition, delta

        return (bestGoodieDef, bestDelta)

    def getFirstGoodie(self, target, resource):
        for goodie in self.actualGoodies.itervalues():
            goodieDefinition = self.definedGoodies[goodie.uid]
            if goodieDefinition.target == target and goodieDefinition.resource == resource:
                return goodie

        return None

    def isGoodieEnabled(self, target, resource):
        for goodieDefinition in self.definedGoodies.itervalues():
            if goodieDefinition.target == target and goodieDefinition.resource == resource:
                return goodieDefinition.enabled

        return False

    def load(self, goodieID, state, finishTime, counter, expirations):
        try:
            goodieDefinition = self.definedGoodies[goodieID]
        except KeyError:
            raise GoodieException('Goodie is not found', goodieID)

        if not goodieDefinition.enabled:
            self.__updateCallback(goodieDefinition.createDisabledGoodie(counter, expirations), ACTION_REASON_ID.GOODIE_DISABLED, counter)
        else:
            self.__append(goodieDefinition, ACTION_REASON_ID.GOODIE_ENABLED, state, finishTime, counter, expirations)

    def extend(self, goodieID, state, counter, expiryTime):
        goodieDefinition = self.definedGoodies[goodieID]
        if goodieDefinition.isExpirable():
            if not expiryTime:
                LOG_WARNING('Cannot add expirable reserve without a positive expirationTime.')
                return
            expirations = {expiryTime: counter}
        else:
            expirations = {}
        finishTime = 0
        goodie = self.actualGoodies.get(goodieID, None)
        if goodie is not None:
            counter += goodie.counter
            mergeExpirationsInto(goodie.expirations, expirations)
            if goodie.state == GOODIE_STATE.ACTIVE:
                state = GOODIE_STATE.ACTIVE
                finishTime = goodie.finishTime
        self.__append(goodieDefinition, ACTION_REASON_ID.EXTERNAL, state, finishTime, counter, expirations)
        return

    def test(self, target, resources, returnDeltas=False, applyToZero=False):
        return self.__show(target, resources, returnDeltas, applyToZero)

    def apply(self, target, resources, returnDeltas=False, applyToZero=False):
        toUpdate = self.__show(target, resources, returnDeltas, applyToZero)
        for goodieID in toUpdate:
            self.__decrement(goodieID, 1, ACTION_REASON_ID.APPLYING, True)

        return toUpdate

    def evaluate(self, condition):
        result = []
        for defined in self.definedGoodies.itervalues():
            if defined.uid in self.actualGoodies:
                continue
            if defined.condition is not None and defined.condition.check(condition):
                self.__append(defined, ACTION_REASON_ID.UNKNOWN)
                result.append(defined.uid)

        return result

    def expire(self):
        toWithdraw = []
        toExpire = []
        toErase = []
        for goodieID, goodie in self.actualGoodies.iteritems():
            defined = self.definedGoodies[goodieID]
            if defined.isTimeLimited() or goodie.isExpirable():
                if goodie.isActive() and goodie.isEffectFinished():
                    toWithdraw.append(goodieID)
                elif goodie.isExpired():
                    toExpire.append(goodieID)
                elif defined.isPastUseBy():
                    toErase.append(goodieID)

        for goodieID in toWithdraw:
            self.__decrement(goodieID, 1, ACTION_REASON_ID.END_OF_EFFECT, True)

        for goodieID in toExpire:
            self.__expire(goodieID)

        for goodieID in toErase:
            self.__erase(goodieID, ACTION_REASON_ID.USE_BY_HAS_PASSED)

    def activeGoodiesCount(self):
        result = 0
        for goodie in self.actualGoodies.itervalues():
            if goodie.isActive():
                result += 1

        return result

    def activate(self, goodieID):
        goodie = self.actualGoodies.get(goodieID, None)
        if goodie is None:
            LOG_WARNING("Couldn't find goodie by id={}", goodieID)
            return
        elif goodie.isActive():
            LOG_WARNING("Couldn't activate goodie(id={}) because it is already activated!".format(goodieID))
            return
        else:
            defined = self.definedGoodies[goodieID]
            if not defined.isTimeLimited():
                LOG_WARNING("Couldn't activate goodie(id={}) because it has unlimited time!".format(goodieID))
                return
            oldGoodieID = self.actualGoodies.checkResource(goodieID)
            if oldGoodieID is not None:
                if self.actualGoodies.compareByResource(oldGoodieID, goodieID):
                    self.__decrement(oldGoodieID, 1, ACTION_REASON_ID.END_OF_EFFECT, False)
                else:
                    LOG_WARNING("Couldn't activate goodie(id={}) because replacing is forbidden!".format(goodieID))
                    return
            if self.activeGoodiesCount() >= MAX_ACTIVE_BOOSTERS:
                LOG_WARNING("Couldn't activate goodie(id={}) because limit of activated boosters is reached!".format(goodieID))
                return
            goodie = defined.createGoodie(state=GOODIE_STATE.ACTIVE, counter=goodie.counter, expirations=goodie.expirations)
            self.actualGoodies[goodieID] = goodie
            self.__updateCallback(goodie, ACTION_REASON_ID.ACTIVATION, 0)
            return goodie

    def deactivateAll(self):
        active_goodies = [ (goodieID, goodie) for goodieID, goodie in self.actualGoodies.iteritems() if goodie.isActive() ]
        for goodieID, goodie in active_goodies:
            defined = self.definedGoodies[goodieID]
            self.__updateActual(defined, newState=GOODIE_STATE.INACTIVE, newFinishTime=None, newCounter=goodie.counter, newExpirations=goodie.expirations, reasonID=ACTION_REASON_ID.DEACTIVATION)

        return

    def activeIds(self):
        return set(self.__resourceIndex.itervalues())

    def erase(self, goodieID):
        self.__erase(goodieID, ACTION_REASON_ID.EXTERNAL)

    def remove(self, goodieID, count):
        self.__decrement(goodieID, count, ACTION_REASON_ID.EXTERNAL, False)
