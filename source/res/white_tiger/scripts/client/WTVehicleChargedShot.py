# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleChargedShot.py
from WTPrefabActivator import WTPrefabActivator

class WTVehicleChargedShot(WTPrefabActivator):

    def set_isChargedShotActive(self, prev):
        self._updatePrefab()

    def _isAbilityActive(self):
        return self.isChargedShotActive
