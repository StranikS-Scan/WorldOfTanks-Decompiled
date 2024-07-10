# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/gun_components.py
from typing import TYPE_CHECKING, Tuple, Optional
from collections import namedtuple
from items.components import legacy_stuff
from soft_exception import SoftException
from wrapped_reflection_framework import reflectedNamedTuple
from wrapped_reflection_framework import ReflectionMetaclass
if TYPE_CHECKING:
    from items.vehicle_items import Shell
RecoilEffect = reflectedNamedTuple('RecoilEffect', ('lodDist', 'amplitude', 'backoffTime', 'returnTime'))

class GunShot(legacy_stuff.LegacyStuff):
    __slots__ = ('shell', 'defaultPortion', 'piercingPower', 'speed', 'gravity', 'nominalMaxDistance', 'maxDistance', 'maxHeight')
    __metaclass__ = ReflectionMetaclass

    def __init__(self, shell, defaultPortion, piercingPower, speed, gravity, maxDistance, maxHeight):
        super(GunShot, self).__init__()
        self.shell = shell
        self.defaultPortion = defaultPortion
        self.piercingPower = piercingPower
        self.speed = speed
        self.gravity = gravity
        self.nominalMaxDistance = maxDistance
        self.maxDistance = maxDistance
        self.maxHeight = maxHeight

    def __repr__(self):
        return 'GunShot(shell = {}, ppower = {}, speed = {}, gravity = {}, nominalMaxDistance - {}, maxDistance = {}, maxHeight = {}))'.format(self.shell, self.piercingPower, self.speed, self.gravity, self.nominalMaxDistance, self.maxDistance, self.maxHeight)

    def copy(self):
        raise SoftException('Operation "GunShot.copy" is not allowed')


class TemperatureGunParams(object):
    TemperatureGunState = namedtuple('TemperatureGunState', ['temperature', 'modifiers', 'isOverheated'])
    __slots__ = ('states', 'heatingPerSec', 'heatingPerShot', 'coolingDelay', 'coolingPerSec', 'coolingOverheatPerSec', 'thermalStateHysteresis', 'temperatureSegmentSize')

    def __init__(self, states, heatingPerSec, heatingPerShot, coolingDelay, coolingPerSec, coolingOverheatPerSec, thermalStateHysteresis, temperatureSegmentSize):
        self.states = states
        self.heatingPerSec = heatingPerSec
        self.heatingPerShot = heatingPerShot
        self.coolingDelay = coolingDelay
        self.coolingPerSec = coolingPerSec
        self.coolingOverheatPerSec = coolingOverheatPerSec
        self.thermalStateHysteresis = thermalStateHysteresis
        self.temperatureSegmentSize = temperatureSegmentSize

    def __repr__(self):
        return 'TemperatureGunParams(states = {}, heatingPerSec = {}, heatingPerShot = {}, coolingDelay = {}, coolingPerSec = {}, coolingOverheatPerSec = {}, thermalStateHysteresis = {}, temperatureSegmentSize = {}))'.format(self.states, self.heatingPerSec, self.heatingPerShot, self.coolingDelay, self.coolingPerSec, self.coolingOverheatPerSec, self.thermalStateHysteresis, self.temperatureSegmentSize)
