# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StorageCategoryBlueprintsViewMeta.py
from gui.Scaleform.daapi.view.lobby.storage.vehicle_view import VehicleView

class StorageCategoryBlueprintsViewMeta(VehicleView):

    def navigateToBlueprintScreen(self, itemId):
        self._printOverrideError('navigateToBlueprintScreen')

    def selectConvertible(self, value):
        self._printOverrideError('selectConvertible')

    def as_updateIntelligenceDataS(self, data):
        return self.flashObject.as_updateIntelligenceData(data) if self._isDAAPIInited() else None

    def as_updateNationalFragmentsS(self, fragments):
        return self.flashObject.as_updateNationalFragments(fragments) if self._isDAAPIInited() else None
