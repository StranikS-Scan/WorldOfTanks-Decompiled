# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/legacy/limits.py
from gui.prb_control.entities.base.limits import LimitsCollection, VehicleIsValid, TeamIsValid

class LegacyLimits(LimitsCollection):
    """
    Class for legacy entities limits.
    """

    def __init__(self, entity):
        super(LegacyLimits, self).__init__(entity, (VehicleIsValid(),), (TeamIsValid(),))
