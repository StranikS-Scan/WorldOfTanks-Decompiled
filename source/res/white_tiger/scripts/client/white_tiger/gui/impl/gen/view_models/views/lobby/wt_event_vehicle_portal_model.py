# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_event_vehicle_portal_model.py
from enum import Enum
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_portal_awards_base_model import WtEventPortalAwardsBaseModel

class EventTankType(Enum):
    PRIMARY = 'G168_KJpz_T_III'
    SECONDARY = 'R212_Object_265T'
    MAIN = 'Pl26_Czolg_P_Wz_46'
    BOSS = 'Pl26_Czolg_P_Wz_46_Verbesserter'


class WtEventVehiclePortalModel(WtEventPortalAwardsBaseModel):
    __slots__ = ('onVideoStarted', 'onPortalRewardsStarted')

    def __init__(self, properties=11, commands=7):
        super(WtEventVehiclePortalModel, self).__init__(properties=properties, commands=commands)

    def getShowVideoName(self):
        return self._getString(8)

    def setShowVideoName(self, value):
        self._setString(8, value)

    def getIdleVideoName(self):
        return self._getString(9)

    def setIdleVideoName(self, value):
        self._setString(9, value)

    def getIsWindowAccessible(self):
        return self._getBool(10)

    def setIsWindowAccessible(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(WtEventVehiclePortalModel, self)._initialize()
        self._addStringProperty('showVideoName', '')
        self._addStringProperty('idleVideoName', '')
        self._addBoolProperty('isWindowAccessible', True)
        self.onVideoStarted = self._addCommand('onVideoStarted')
        self.onPortalRewardsStarted = self._addCommand('onPortalRewardsStarted')
