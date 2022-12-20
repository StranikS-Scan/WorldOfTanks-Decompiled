# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/Goodies.py
import collections
from typing import TYPE_CHECKING
from WeakMethod import WeakMethod
from debug_utils import LOG_WARNING
from goodie_constants import GOODIE_STATE, MAX_ACTIVE_BOOSTERS, GOODIE_NOTIFICATION_TYPE
from soft_exception import SoftException
from GoodieResources import GoodieResource
from GoodieTargets import GoodieTarget
if TYPE_CHECKING:
    from typing import Type, Dict, Optional, Callable
    from goodies.Goodie import Goodie
    from goodies.GoodieDefinition import GoodieDefinition

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

    def __updateCallback(self, goodie, notificationType=GOODIE_NOTIFICATION_TYPE.EMPTY):
        if self._updateCallback is not None:
            callbackRef = self._updateCallback()
            if callbackRef:
                callbackRef(goodie, notificationType)
        return

    def __removeCallback(self, goodieID):
        if self._removeCallback is not None:
            callbackRef = self._removeCallback()
            if callbackRef:
                callbackRef(goodieID)
        return

    def __append(self, goodieDefinition, state=None, expiration=None, counter=None, notificationType=GOODIE_NOTIFICATION_TYPE.EMPTY):
        goodie = goodieDefinition.createGoodie(state, expiration, counter)
        if goodie is None:
            return
        else:
            self.actualGoodies[goodieDefinition.uid] = goodie
            self.__updateCallback(goodie, notificationType)
            return

    def __erase(self, goodieID):
        goodie = self.actualGoodies.get(goodieID, None)
        if goodie is None:
            return
        else:
            del self.actualGoodies[goodieID]
            self.__removeCallback(goodieID)
            return

    def __updateCounter(self, goodieDefinition, counter, state=None, notificationType=GOODIE_NOTIFICATION_TYPE.REMOVED):
        goodie = goodieDefinition.createGoodie(counter=counter, state=state)
        if goodie is None:
            return
        else:
            self.actualGoodies[goodieDefinition.uid] = goodie
            self.__updateCallback(goodie, notificationType)
            return

    def __update(self, goodieID):
        goodieDefinition = self.definedGoodies.get(goodieID, None)
        if goodieDefinition is None:
            return
        else:
            goodie = self.actualGoodies.get(goodieID, None)
            if goodie is None:
                return
            if goodieDefinition.isActivatable() and goodie.isActive() and not goodie.isExpired():
                return
            self.remove(goodieID, goodie, goodieDefinition)
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

    def load(self, goodieID, state, expiration, counter):
        try:
            goodieDefinition = self.definedGoodies[goodieID]
        except KeyError:
            raise GoodieException('Goodie is not found', goodieID)

        if not goodieDefinition.enabled:
            self.__updateCallback(goodieDefinition.createDisabledGoodie(counter), GOODIE_NOTIFICATION_TYPE.DISABLED)
        else:
            self.__append(goodieDefinition, state, expiration, counter, GOODIE_NOTIFICATION_TYPE.ENABLED)

    def extend(self, goodieID, state, expiration, counter):
        goodieDefinition = self.definedGoodies[goodieID]
        goodie = self.actualGoodies.get(goodieID, None)
        if goodie is not None:
            counter += goodie.counter
            if goodie.state == GOODIE_STATE.ACTIVE:
                state = GOODIE_STATE.ACTIVE
                expiration = goodie.expiration
        self.__append(goodieDefinition, state, expiration, counter)
        return

    def test(self, target, resources, returnDeltas=False, applyToZero=False):
        return self.__show(target, resources, returnDeltas, applyToZero)

    def apply(self, target, resources, returnDeltas=False, applyToZero=False):
        toUpdate = self.__show(target, resources, returnDeltas, applyToZero)
        for goodieID in toUpdate:
            self.__update(goodieID)

        return toUpdate

    def evaluate(self, condition):
        result = []
        for defined in self.definedGoodies.itervalues():
            if defined.uid in self.actualGoodies:
                continue
            if defined.condition is not None and defined.condition.check(condition):
                self.__append(defined)
                result.append(defined.uid)

        return result

    def expire(self):
        toUpdate = []
        toRemove = []
        for goodieID, goodie in self.actualGoodies.iteritems():
            defined = self.definedGoodies[goodieID]
            if defined.isTimeLimited():
                if defined.isExpired():
                    toRemove.append(goodieID)
                elif goodie.isActive() and goodie.isExpired():
                    toUpdate.append(goodieID)

        for goodieID in toUpdate:
            self.__update(goodieID)

        for goodieID in toRemove:
            self.__erase(goodieID)

        return len(toRemove) != 0 or len(toUpdate) != 0

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
                    self.remove(oldGoodieID)
                else:
                    LOG_WARNING("Couldn't activate goodie(id={}) because replacing is forbidden!".format(goodieID))
                    return
            if self.activeGoodiesCount() >= MAX_ACTIVE_BOOSTERS:
                LOG_WARNING("Couldn't activate goodie(id={}) because limit of activated boosters is reached!".format(goodieID))
                return
            goodie = defined.createGoodie(state=GOODIE_STATE.ACTIVE, counter=goodie.counter)
            self.actualGoodies[goodieID] = goodie
            self.__updateCallback(goodie)
            return goodie

    def deactivateAll(self):
        active_goodies = [ (goodieID, goodie) for goodieID, goodie in self.actualGoodies.iteritems() if goodie.isActive() ]
        for goodieID, goodie in active_goodies:
            defined = self.definedGoodies[goodieID]
            self.__updateCounter(defined, goodie.counter, GOODIE_STATE.INACTIVE, GOODIE_NOTIFICATION_TYPE.DISABLED)

    def activeIds(self):
        return set(self.__resourceIndex.itervalues())

    def erase(self, goodieID):
        goodie = self.actualGoodies.get(goodieID, None)
        if goodie is None:
            return
        else:
            self.__erase(goodieID)
            return

    def remove(self, goodieID, goodie=None, goodieDefinition=None, count=1):
        if goodie is None:
            goodie = self.actualGoodies.get(goodieID, None)
            if goodie is None:
                return
        if goodieDefinition is None:
            goodieDefinition = self.definedGoodies.get(goodieID, None)
            if goodieDefinition is None:
                return
        counter = goodie.counter - count
        if counter <= 0:
            self.__erase(goodieID)
        else:
            self.__updateCounter(goodieDefinition, counter)
        return
