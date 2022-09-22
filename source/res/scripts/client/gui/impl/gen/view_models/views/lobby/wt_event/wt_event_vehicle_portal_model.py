# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_vehicle_portal_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_awards_base_model import WtEventPortalAwardsBaseModel

class EventTankType(Enum):
    PRIMARY = 'R121_KV4_KTT'
    SECONDARY = 'GB110_FV4201_Chieftain_Prototype'


class WtEventVehiclePortalModel(WtEventPortalAwardsBaseModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=5):
        super(WtEventVehiclePortalModel, self).__init__(properties=properties, commands=commands)

    def getEventTank(self):
        return EventTankType(self._getString(8))

    def setEventTank(self, value):
        self._setString(8, value.value)

    def _initialize(self):
        super(WtEventVehiclePortalModel, self)._initialize()
        self._addStringProperty('eventTank')
