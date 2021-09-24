# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_vehicle_portal_model.py
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_awards_base_model import WtEventPortalAwardsBaseModel

class WtEventVehiclePortalModel(WtEventPortalAwardsBaseModel):
    __slots__ = ('onShowAllRewards',)

    def __init__(self, properties=6, commands=5):
        super(WtEventVehiclePortalModel, self).__init__(properties=properties, commands=commands)

    def getIsFromMultipleOpening(self):
        return self._getBool(5)

    def setIsFromMultipleOpening(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(WtEventVehiclePortalModel, self)._initialize()
        self._addBoolProperty('isFromMultipleOpening', False)
        self.onShowAllRewards = self._addCommand('onShowAllRewards')
