# Embedded file name: scripts/common/goodies/Goodies.py
from WeakMethod import WeakMethod
from goodie_constants import GOODIE_STATE, MAX_ACTIVE_GOODIES
from debug_utils import LOG_AQ

class Goodies(object):

    def __init__(self, definedGoodies, updateCallback = None, removeCallback = None):
        self.definedGoodies = definedGoodies
        self.actualGoodies = {}
        if updateCallback:
            self._updateCallback = WeakMethod(updateCallback)
        else:
            self._updateCallback = None
        if removeCallback:
            self._removeCallback = WeakMethod(removeCallback)
        else:
            self._removeCallback = None
        return

    def __updateCallback(self, goodie):
        if self._updateCallback is not None:
            callbackRef = self._updateCallback()
            if callbackRef:
                callbackRef(goodie)
        return

    def __removeCallback(self, goodieId):
        if self._removeCallback is not None:
            callbackRef = self._removeCallback()
            if callbackRef:
                callbackRef(goodieId)
        return

    def __append(self, goodieDefinition, state = None, expiration = None, counter = None):
        goodie = goodieDefinition.createGoodie(state, expiration, counter)
        if goodie is None:
            return
        else:
            self.actualGoodies[goodieDefinition.uid] = goodie
            self.__updateCallback(goodie)
            return

    def __remove(self, goodieId):
        goodie = self.actualGoodies.get(goodieId, None)
        if goodie is None:
            return
        else:
            del self.actualGoodies[goodieId]
            self.__removeCallback(goodieId)
            return

    def __updateCounter(self, goodieDefinition, counter):
        goodie = goodieDefinition.createGoodie(counter=counter)
        if goodie is None:
            return
        else:
            self.actualGoodies[goodieDefinition.uid] = goodie
            self.__updateCallback(goodie)
            return

    def __update(self, goodieId):
        goodieDefinition = self.definedGoodies.get(goodieId, None)
        if goodieDefinition is None:
            return
        else:
            goodie = self.actualGoodies.get(goodieId, None)
            if goodie is None:
                return
            if goodieDefinition.isActivatable() and goodie.isActive() and not goodie.isExpired():
                return
            counter = self.actualGoodies[goodieId].counter - 1
            if counter <= 0:
                self.__remove(goodieId)
            else:
                self.__updateCounter(goodieDefinition, counter)
            return

    def __checkDuplicateResources(self, allResourcesByType, affectedResources):
        for r in affectedResources:
            if r.__class__ in allResourcesByType:
                return True
            allResourcesByType.add(r.__class__)

        return False

    def __show(self, target, resources, returnDeltas):
        toUpdate = []
        result = set()
        allResourcesByType = set()
        for goodie in self.actualGoodies.itervalues():
            goodieDefinition = self.definedGoodies[goodie.uid]
            if goodieDefinition.isActivatable() and not goodie.isActive():
                continue
            if goodieDefinition.target == target:
                if returnDeltas:
                    affectedResources = goodieDefinition.apply_delta(resources)
                else:
                    affectedResources = goodieDefinition.apply(resources)
                if not self.__checkDuplicateResources(allResourcesByType, affectedResources):
                    result.update(affectedResources)
                    toUpdate.append(goodie.uid)

        return (result, toUpdate)

    def actual(self):
        return self.actualGoodies.itervalues()

    def actualIds(self):
        return set(self.actualGoodies.iterkeys())

    def load(self, goodieId, state, expiration, counter):
        goodieDefinition = self.definedGoodies[goodieId]
        self.__append(goodieDefinition, state, expiration, counter)

    def extend(self, goodieId, state, expiration, counter):
        goodieDefinition = self.definedGoodies[goodieId]
        goodie = self.actualGoodies.get(goodieId, None)
        if goodie is not None:
            counter += goodie.counter
            if goodie.state == GOODIE_STATE.ACTIVE:
                state = GOODIE_STATE.ACTIVE
                expiration = goodie.expiration
        self.__append(goodieDefinition, state, expiration, counter)
        return

    def test(self, target, resource, returnDeltas = False):
        return self.__show(target, resource, returnDeltas)[0]

    def apply(self, target, resources, returnDeltas = False):
        affectedResources, toUpdate = self.__show(target, resources, returnDeltas)
        for goodieId in toUpdate:
            self.__update(goodieId)

        return affectedResources

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
        for goodieId, goodie in self.actualGoodies.iteritems():
            defined = self.definedGoodies[goodieId]
            if defined.isTimeLimited():
                if defined.isExpired():
                    toRemove.append(goodieId)
                elif goodie.isExpired():
                    toUpdate.append(goodieId)

        for goodieId in toUpdate:
            self.__update(goodieId)

        for goodieId in toRemove:
            self.__remove(goodieId)

        return len(toRemove) != 0 or len(toUpdate) != 0

    def activeGoodiesCount(self):
        result = 0
        for goodie in self.actualGoodies.itervalues():
            if goodie.isActive():
                result += 1

        return result

    def activate(self, goodieId):
        if self.activeGoodiesCount() > MAX_ACTIVE_GOODIES:
            return
        else:
            goodie = self.actualGoodies.get(goodieId, None)
            if goodie is None:
                return
            if goodie.isActive():
                return
            defined = self.definedGoodies[goodieId]
            if not defined.isTimeLimited():
                return
            goodie = defined.createGoodie(state=GOODIE_STATE.ACTIVE, counter=goodie.counter)
            self.actualGoodies[goodieId] = goodie
            self.__updateCallback(goodie)
            return goodie

    def remove(self, goodieId):
        goodie = self.actualGoodies.get(goodieId, None)
        if goodie is None:
            return
        else:
            self.__remove(goodieId)
            return
