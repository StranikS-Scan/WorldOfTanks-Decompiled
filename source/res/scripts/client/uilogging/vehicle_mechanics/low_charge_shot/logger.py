# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/vehicle_mechanics/low_charge_shot/logger.py
from uilogging.base.logger import MetricsLogger
from uilogging.constants import CommonLogActions
from uilogging.vehicle_mechanics.low_charge_shot.constants import FEATURE_LOW_CHARGE_SHOT, LOW_CHARGE_SHOT_SCREEN, LowChargeShotItems

class LowChargeShotUILogger(MetricsLogger):

    def __init__(self):
        super(LowChargeShotUILogger, self).__init__(FEATURE_LOW_CHARGE_SHOT)

    def onAlmostFinishedStarted(self):
        self.startAction(CommonLogActions.CLICK)

    def onAlmostFinishedEnded(self):
        self.reset()

    def onAlmostFinishedClicked(self, arenaUniqueID):
        self.stopAction(action=CommonLogActions.CLICK, item=LowChargeShotItems.AIMING_CIRCLE, info=str(arenaUniqueID), parentScreen=LOW_CHARGE_SHOT_SCREEN)
