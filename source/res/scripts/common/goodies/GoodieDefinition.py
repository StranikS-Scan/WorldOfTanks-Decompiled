# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/GoodieDefinition.py
import time
from typing import TYPE_CHECKING
from Goodie import Goodie
from goodie_constants import GOODIE_VARIETY, GOODIE_STATE
from soft_exception import SoftException
if TYPE_CHECKING:
    from typing import Optional
    from goodies.GoodieConditions import Condition
    from goodies.GoodieResources import GoodieResource
    from goodies.GoodieTargets import GoodieTarget
    from goodies.GoodieValue import GoodieValue

class OverLimitException(SoftException):
    pass


class GoodieDefinition(object):
    __slots__ = ['uid',
     'variety',
     'target',
     'enabled',
     'lifetime',
     'useby',
     'counter',
     'autostart',
     'resource',
     'value',
     'condition']

    def __init__(self, uid, variety, target, enabled, lifetime, useby, counter, autostart, resource, value, condition):
        self.uid = uid
        self.variety = variety
        self.target = target
        self.enabled = enabled
        self.lifetime = lifetime
        self.useby = useby
        self.counter = counter
        self.autostart = autostart
        self.resource = resource
        self.value = value
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

    def apply(self, resources, applyToZero):
        if not isinstance(resources, set):
            resources = {resources}
        for resource in resources:
            if resource.value == 0 and not applyToZero:
                continue
            if resource.__class__ == self.resource:
                if self.variety in GOODIE_VARIETY.DISCOUNT_LIKE:
                    result = self.value.reduce(resource.value)
                    if self.target.limit is not None and resource.value - result > self.target.limit:
                        raise OverLimitException('Discount is over the limit' % self.target.limit)
                    else:
                        return resource.__class__(result)
                else:
                    if self.variety == GOODIE_VARIETY.BOOSTER:
                        return resource.__class__(self.value.increase(resource.value))
                    raise SoftException('Programming error, Goodie is not a discount or booster' % self.variety)

        return

    def apply_delta(self, resource, applyToZero):
        if resource.value == 0 and not applyToZero:
            return None
        else:
            return resource.__class__(self.value.delta(resource.value)) if resource.__class__ == self.resource else None

    def createGoodie(self, state=None, expiration=None, counter=None):
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
                        if self.useby is None:
                            expiration = time.time() + self.lifetime
                        else:
                            expiration = min(time.time() + self.lifetime, self.useby)
                    else:
                        expiration = 0
            else:
                expiration = 0
            if counter is None:
                counter = self.counter
            return Goodie(self.uid, state, expiration, counter)

    def createDisabledGoodie(self, counter):
        return Goodie(self.uid, GOODIE_STATE.INACTIVE, 0, counter)
