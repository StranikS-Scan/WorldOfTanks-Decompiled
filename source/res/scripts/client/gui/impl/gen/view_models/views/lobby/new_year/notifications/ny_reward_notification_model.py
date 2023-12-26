# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/ny_reward_notification_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.reward_item_model import RewardItemModel

class NyRewardNotificationModel(RewardItemModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(NyRewardNotificationModel, self).__init__(properties=properties, commands=commands)

    def getIntCD(self):
        return self._getNumber(14)

    def setIntCD(self, value):
        self._setNumber(14, value)

    def getVehicleLvl(self):
        return self._getString(15)

    def setVehicleLvl(self, value):
        self._setString(15, value)

    def getVehicleName(self):
        return self._getString(16)

    def setVehicleName(self, value):
        self._setString(16, value)

    def getLevel(self):
        return self._getNumber(17)

    def setLevel(self, value):
        self._setNumber(17, value)

    def getSelectedVehicle(self):
        return self._getString(18)

    def setSelectedVehicle(self, value):
        self._setString(18, value)

    def _initialize(self):
        super(NyRewardNotificationModel, self)._initialize()
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('vehicleLvl', '')
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('level', 0)
        self._addStringProperty('selectedVehicle', '')
