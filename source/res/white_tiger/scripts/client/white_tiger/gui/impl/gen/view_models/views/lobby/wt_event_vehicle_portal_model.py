# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_event_vehicle_portal_model.py
from enum import Enum
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_portal_awards_base_model import WtEventPortalAwardsBaseModel

class EventTankType(Enum):
    PRIMARY = 'G168_KJpz_T_III'
    SECONDARY = 'R191_Object_283'
    MAIN = 'Pl26_Czolg_P_Wz_46'
    BOSS = 'R33_Churchill_LL'


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
