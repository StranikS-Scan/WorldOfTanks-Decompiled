# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/ny_reward_notification_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.reward_item_model import RewardItemModel

class NyRewardNotificationModel(RewardItemModel):
    __slots__ = ()

    def __init__(self, properties=21, commands=0):
        super(NyRewardNotificationModel, self).__init__(properties=properties, commands=commands)

    def getIntCD(self):
        return self._getNumber(16)

    def setIntCD(self, value):
        self._setNumber(16, value)

    def getVehicleLvl(self):
        return self._getString(17)

    def setVehicleLvl(self, value):
        self._setString(17, value)

    def getVehicleName(self):
        return self._getString(18)

    def setVehicleName(self, value):
        self._setString(18, value)

    def getLevel(self):
        return self._getNumber(19)

    def setLevel(self, value):
        self._setNumber(19, value)

    def getSelectedVehicle(self):
        return self._getString(20)

    def setSelectedVehicle(self, value):
        self._setString(20, value)

    def _initialize(self):
        super(NyRewardNotificationModel, self)._initialize()
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('vehicleLvl', '')
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('selectedVehicle', '')
