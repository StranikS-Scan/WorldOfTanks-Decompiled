# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/recruit_new_tankman_dialog_model.py
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel

class RecruitNewTankmanDialogModel(DialogTemplateViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=2):
        super(RecruitNewTankmanDialogModel, self).__init__(properties=properties, commands=commands)

    def getRole(self):
        return self._getString(6)

    def setRole(self, value):
        self._setString(6, value)

    def getVehicleName(self):
        return self._getString(7)

    def setVehicleName(self, value):
        self._setString(7, value)

    def getVehicleType(self):
        return self._getString(8)

    def setVehicleType(self, value):
        self._setString(8, value)

    def getVehicleLevel(self):
        return self._getNumber(9)

    def setVehicleLevel(self, value):
        self._setNumber(9, value)

    def getIsPremium(self):
        return self._getBool(10)

    def setIsPremium(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(RecruitNewTankmanDialogModel, self)._initialize()
        self._addStringProperty('role', '')
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('vehicleLevel', 0)
        self._addBoolProperty('isPremium', False)
