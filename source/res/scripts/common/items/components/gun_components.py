# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/gun_components.py
from collections import namedtuple
from items.components import legacy_stuff
from soft_exception import SoftException
from wrapped_reflection_framework import reflectedNamedTuple
from wrapped_reflection_framework import ReflectionMetaclass
RecoilEffect = reflectedNamedTuple('RecoilEffect', ('lodDist', 'amplitude', 'backoffTime', 'returnTime'))
SpinEffect = namedtuple('SpinEffect', ('activationSound', 'deactivationSound'))

class GunShot(legacy_stuff.LegacyStuff):
    __slots__ = ('shell', 'defaultPortion', 'piercingPower', 'speed', 'gravity', 'maxDistance', 'maxHeight')
    __metaclass__ = ReflectionMetaclass

    def __init__(self, shell, defaultPortion, piercingPower, speed, gravity, maxDistance, maxHeight):
        super(GunShot, self).__init__()
        self.shell = shell
        self.defaultPortion = defaultPortion
        self.piercingPower = piercingPower
        self.speed = speed
        self.gravity = gravity
        self.maxDistance = maxDistance
        self.maxHeight = maxHeight

    def __repr__(self):
        return 'GunShot(shell = {}, ppower = {}, speed = {}, gravity = {}, maxDistance = {}, maxHeight = {}))'.format(self.shell, self.piercingPower, self.speed, self.gravity, self.maxDistance, self.maxHeight)

    def copy(self):
        raise SoftException('Operation "GunShot.copy" is not allowed')


class TemperatureGunParams(object):
    TemperatureGunState = namedtuple('TemperatureGunState', ['temperature',
     'modifiers',
     'isOverheated',
     'heatingPerShot',
     'heatingPerSec',
     'coolingPerSec',
     'coolingOverheatPerSec',
     'coolingDelay'])
    __slots__ = ('states', 'temperatureThresholds', 'temperatureSegmentSize')

    def __init__(self, states, temperatureThresholds, temperatureSegmentSize):
        self.states = states
        self.temperatureThresholds = temperatureThresholds
        self.temperatureSegmentSize = temperatureSegmentSize

    def __repr__(self):
        return 'TemperatureGunParams(states = {}, temperatureThresholds = {}, temperatureSegmentSize = {}))'.format(self.states, self.temperatureThresholds, self.temperatureSegmentSize)
