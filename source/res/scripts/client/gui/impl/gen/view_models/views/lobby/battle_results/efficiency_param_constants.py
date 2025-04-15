# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/efficiency_param_constants.py
from frameworks.wulf import ViewModel

class EfficiencyParamConstants(ViewModel):
    __slots__ = ()
    KILLS = 'kills'
    SPOTTED = 'spotted'
    DAMAGE_DEALT = 'damageDealt'
    STUN = 'damageAssistedStun'
    DAMAGE_ASSISTED = 'damageAssisted'
    DAMAGE_BLOCKED_BY_ARMOR = 'damageBlockedByArmor'
    CAPTURE_POINTS = 'capturePoints'
    DROPPED_CAPTURE_POINTS = 'droppedCapturePoints'

    def __init__(self, properties=0, commands=0):
        super(EfficiencyParamConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(EfficiencyParamConstants, self)._initialize()
