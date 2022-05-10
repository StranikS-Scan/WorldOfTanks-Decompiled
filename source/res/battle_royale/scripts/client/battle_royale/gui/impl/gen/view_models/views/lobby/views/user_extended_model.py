# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/user_extended_model.py
from battle_royale.gui.impl.gen.view_models.views.lobby.views.user_model import UserModel

class UserExtendedModel(UserModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(UserExtendedModel, self).__init__(properties=properties, commands=commands)

    def getVehicleType(self):
        return self._getString(3)

    def setVehicleType(self, value):
        self._setString(3, value)

    def getVehicleName(self):
        return self._getString(4)

    def setVehicleName(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(UserExtendedModel, self)._initialize()
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('vehicleName', '')
