# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/vehicle_info_intro_overlay_model.py
from frameworks.wulf import ViewModel

class VehicleInfoIntroOverlayModel(ViewModel):
    __slots__ = ('onSubmitBtnClick',)

    def __init__(self, properties=2, commands=1):
        super(VehicleInfoIntroOverlayModel, self).__init__(properties=properties, commands=commands)

    def getVehicleTag(self):
        return self._getString(0)

    def setVehicleTag(self, value):
        self._setString(0, value)

    def getIsFirstView(self):
        return self._getBool(1)

    def setIsFirstView(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(VehicleInfoIntroOverlayModel, self)._initialize()
        self._addStringProperty('vehicleTag', '')
        self._addBoolProperty('isFirstView', False)
        self.onSubmitBtnClick = self._addCommand('onSubmitBtnClick')
