# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/auto_shoot_guns/auto_shoot_helpers.py
import BigWorld
from auto_shoot_guns.auto_shoot_guns_common import BURST_ACTIVATION_MIN_TIMEOUT, BURST_ACTIVATION_MAX_TIMEOUT, BURST_DEACTIVATION_MIN_TIMEOUT, BURST_DEACTIVATION_MAX_TIMEOUT
from gui.shared.utils.functions import clamp

def getBurstActivationTimeout():
    return clamp(BigWorld.LatencyInfo().value[3] * 0.5, BURST_ACTIVATION_MIN_TIMEOUT, BURST_ACTIVATION_MAX_TIMEOUT)


def getBurstDeactivationTimeout():
    return clamp(BigWorld.LatencyInfo().value[3] * 0.5, BURST_DEACTIVATION_MIN_TIMEOUT, BURST_DEACTIVATION_MAX_TIMEOUT)
