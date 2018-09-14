# Embedded file name: scripts/common/goodies/GoodieDefinition.py
import time
from Goodie import Goodie
from goodie_constants import GOODIE_VARIETY, GOODIE_STATE

class GoodieDefinition(object):
    __slots__ = ['uid',
     'variety',
     'target',
     'enabled',
     'lifetime',
     'useby',
     'counter',
     'autostart',
     'value',
     'resources',
     'condition']

    def __init__(self, uid, variety, target, enabled, lifetime, useby, counter, autostart, resources, condition):
        self.uid = uid
        self.variety = variety
        self.target = target
        self.enabled = enabled
        self.lifetime = lifetime
        self.useby = useby
        self.counter = counter
        self.autostart = autostart
        self.resources = resources
        self.condition = condition

    def isActivatable(self):
        return self.lifetime is not None

    def isTimeLimited(self):
        return self.lifetime is not None or self.useby is not None

    def isCountable(self):
        return self.counter != 0

    def isExpired(self):
        if self.useby is not None and self.useby < time.time():
            return True
        else:
            return False
            return

    def apply(self, resources):
        if not isinstance(resources, set):
            resources = {resources}
        result = set()
        for resource in resources:
            value = self.resources.get(resource.__class__, None)
            if value is not None:
                if self.variety == GOODIE_VARIETY.DISCOUNT:
                    result.add(resource.__class__(value.reduce(resource.value)))
                elif self.variety == GOODIE_VARIETY.BOOSTER:
                    result.add(resource.__class__(value.increase(resource.value)))
                else:
                    raise Exception, 'Programming error, Goodie is not a discount or booster' % self.variety

        return result

    def apply_delta(self, resources):
        if not isinstance(resources, set):
            resources = {resources}
        result = set()
        for resource in resources:
            value = self.resources.get(resource.__class__, None)
            if value is not None:
                result.add(resource.__class__(value.delta(resource.value)))

        return result

    def createGoodie(self, state = None, expiration = None, counter = None):
        if not self.enabled:
            return
        else:
            if state is None:
                if self.autostart:
                    state = GOODIE_STATE.ACTIVE
                else:
                    state = GOODIE_STATE.INACTIVE
            if self.isTimeLimited():
                if expiration is None:
                    if state == GOODIE_STATE.ACTIVE:
                        expiration = min(time.time() + self.lifetime, self.useby)
                    else:
                        expiration = 0
            else:
                expiration = 0
            if counter is None:
                counter = self.counter
            return Goodie(self.uid, state, expiration, counter)
