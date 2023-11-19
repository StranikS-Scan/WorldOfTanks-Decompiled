# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/sub_views/frontline_confirm_title_model.py
from frameworks.wulf import ViewModel

class FrontlineConfirmTitleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(FrontlineConfirmTitleModel, self).__init__(properties=properties, commands=commands)

    def getTitleText(self):
        return self._getString(0)

    def setTitleText(self, value):
        self._setString(0, value)

    def getSelectedSkillName(self):
        return self._getString(1)

    def setSelectedSkillName(self, value):
        self._setString(1, value)

    def getVehicleType(self):
        return self._getString(2)

    def setVehicleType(self, value):
        self._setString(2, value)

    def getIsMultipleReserves(self):
        return self._getBool(3)

    def setIsMultipleReserves(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(FrontlineConfirmTitleModel, self)._initialize()
        self._addStringProperty('titleText', '')
        self._addStringProperty('selectedSkillName', '')
        self._addStringProperty('vehicleType', '')
        self._addBoolProperty('isMultipleReserves', False)
