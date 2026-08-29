# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portal_rewards/wt_portal_vehicle_reward_model.py
from white_tiger.gui.impl.gen.view_models.views.lobby.portal_rewards.wt_portal_rewards_base_model import WtPortalRewardsBaseModel

class WtPortalVehicleRewardModel(WtPortalRewardsBaseModel):
    __slots__ = ('onIntroVideoPlay', 'onVehicleVideoComplete', 'onVideoInterrupt')

    def __init__(self, properties=9, commands=7):
        super(WtPortalVehicleRewardModel, self).__init__(properties=properties, commands=commands)

    def getIntroVideoName(self):
        return self._getString(4)

    def setIntroVideoName(self, value):
        self._setString(4, value)

    def getVehicleVideoName(self):
        return self._getString(5)

    def setVehicleVideoName(self, value):
        self._setString(5, value)

    def getIsWindowAccessible(self):
        return self._getBool(6)

    def setIsWindowAccessible(self, value):
        self._setBool(6, value)

    def getIsLastVideo(self):
        return self._getBool(7)

    def setIsLastVideo(self, value):
        self._setBool(7, value)

    def getRemainingVideoNumber(self):
        return self._getNumber(8)

    def setRemainingVideoNumber(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(WtPortalVehicleRewardModel, self)._initialize()
        self._addStringProperty('introVideoName', '')
        self._addStringProperty('vehicleVideoName', '')
        self._addBoolProperty('isWindowAccessible', True)
        self._addBoolProperty('isLastVideo', False)
        self._addNumberProperty('remainingVideoNumber', 0)
        self.onIntroVideoPlay = self._addCommand('onIntroVideoPlay')
        self.onVehicleVideoComplete = self._addCommand('onVehicleVideoComplete')
        self.onVideoInterrupt = self._addCommand('onVideoInterrupt')
