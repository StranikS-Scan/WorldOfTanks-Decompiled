# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/auto_shoot_guns/auto_shoot_guns_common.py
from constants import SERVER_TICK_LENGTH
DISCRETE_SHOOTING_THRESHOLD = 0.25
BURST_VERIFYING_DELTA = 0.0
BURST_CONFIRMATION_DELTA = 0.5
BURST_CONFIRMATION_TIMEOUT = BURST_CONFIRMATION_DELTA * 4
PROJECTILE_LOG_FREQUENCY_LIMIT = 10
ASSIST_LOG_FREQUENCY_TIMEOUT = 1.0
COMBAT_ACTIONS_DELAY = 1.0

class PROJECTILE_INTERVAL_SETTINGS:
    PROJECTILE_INTERVAL_LIMITS = [0, 8, 16]
    DEFAULT_PROJECTILE_INTERVAL = SERVER_TICK_LENGTH


class AutoShootGunState(object):
    NONE = 0
    CONTINUOUS_SHOOTING = 1
    DISCRETE_SHOOTING = 2
    DELAY_SHOOT = 3
    NOT_SHOOT = 4
    SHOOTING_STATES = (CONTINUOUS_SHOOTING, DISCRETE_SHOOTING)
    NAMES = {NONE: 'none',
     CONTINUOUS_SHOOTING: 'continuous_shooting',
     DISCRETE_SHOOTING: 'discrete_shooting',
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


def autoShootDynamicAttrFactors():
    factors = {'rate/multiplier': 1.0,
     'isDelayShooting': False,
     'shotDispersionPerSecFactor': 1.0,
     'maxShotDispersionFactor': 1.0,
     'projectileIntervalFactor': 1.0}
    return factors
