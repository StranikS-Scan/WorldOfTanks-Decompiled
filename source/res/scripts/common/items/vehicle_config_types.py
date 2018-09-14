# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/vehicle_config_types.py
from collections import namedtuple
LodSettings = namedtuple('LodSettings', ['maxLodDistance', 'maxPriority'])
LeveredSuspensionConfig = namedtuple('LeveredSuspensionConfig', ['levers', 'interpolationSpeedMul', 'lodSettings'])
SuspensionLever = namedtuple('SuspensionLever', ['startNodeName',
 'jointNodeName',
 'trackNodeName',
 'minAngle',
 'maxAngle'])
SoundSiegeModeStateChange = namedtuple('SoundSiegeModeStateChange', ['on', 'off'])
