# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/auto_shoot_guns/auto_shoot_guns_common.py
PROJECTILE_INTERVAL = 0.1
BURST_ACTIVATION_MIN_TIMEOUT = 0.0
BURST_ACTIVATION_MAX_TIMEOUT = 1.0
BURST_DEACTIVATION_MIN_TIMEOUT = 0.0
BURST_DEACTIVATION_MAX_TIMEOUT = 1.0
BURST_VERIFYING_DELTA = 0.0
BURST_CONFIRMATION_DELTA = 0.5
BURST_CONFIRMATION_TIMEOUT = BURST_CONFIRMATION_DELTA * 4
CLIP_MAX_INTERVAL = PROJECTILE_INTERVAL
CLIP_MIN_RATE = 1.0 / CLIP_MAX_INTERVAL

class AutoShootGunState(object):
    NONE = 0
    SHOOT = 1
    DELAY_SHOOT = 2
    NOT_SHOOT = 3
    SHOOTING_STATES = (SHOOT, DELAY_SHOOT)
    NAMES = {NONE: 'none',
     SHOOT: 'shoot',
     DELAY_SHOOT: 'delay_shoot',
     NOT_SHOOT: 'not_shoot'}


class AutoShootPredictionState(object):
    NOT_ACTIVE = 0
    ACTIVATION = 1
    ACTIVE = 2
    DEACTIVATION = 3
    COOLDOWN = 4
    ACTIVATED = (ACTIVE, DEACTIVATION)
    CONFIRMABLE = (NOT_ACTIVE, ACTIVE)
    COOLDOWNABLE = (ACTIVATION, ACTIVE, DEACTIVATION)
    DISABLEABLE = (ACTIVATION, ACTIVE)
    NAMES = {NOT_ACTIVE: 'not_active',
     ACTIVATION: 'activation',
     ACTIVE: 'active',
     DEACTIVATION: 'deactivation',
     COOLDOWN: 'cooldown'}


class SpinGunState(object):
    NOT_STARTED = 0
    SPIN_UP = 1
    SPIN_FULL = 2
    SPIN_DOWN = 3
    ACTIVE_STATES = (SPIN_FULL, SPIN_UP, SPIN_DOWN)
    DYNAMIC_STATES = (SPIN_UP, SPIN_DOWN)


def autoShootDynamicAttrFactors():
    factors = {'rate/multiplier': 1.0,
     'isDelayShooting': False,
     'shotDispersionPerSecFactor': 1.0,
     'maxShotDispersionFactor': 1.0}
    return factors
