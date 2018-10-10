# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vibroeffects/Controllers/RammingController.py
import BigWorld
from OnceController import OnceController
from constants import DESTRUCTIBLE_MATKIND

class RammingController(object):
    RAMMING_EXECUTION_DELAY = 2.5
    MIN_IMPACT_SPEED = 3
    __executionForbidden = None

    def __allowExecution(self):
        self.__executionForbidden = None
        return

    def destroy(self):
        if self.__executionForbidden is not None:
            BigWorld.cancelCallback(self.__executionForbidden)
        return

    def execute(self, vehicleSpeed, matKind):
        effectName = not self.__executionForbidden and vehicleSpeed >= self.MIN_IMPACT_SPEED and 'ramming_vehicle_veff'
        if matKind is not None:
            if DESTRUCTIBLE_MATKIND.MIN <= matKind <= DESTRUCTIBLE_MATKIND.MAX:
                effectName = 'ramming_destructible_veff'
            else:
                effectName = 'ramming_indestructible_veff'
            OnceController(effectName)
            self.__executionForbidden = BigWorld.callback(self.RAMMING_EXECUTION_DELAY, self.__allowExecution)
        return
