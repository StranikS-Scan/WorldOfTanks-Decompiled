# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/convert_window_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_model import DetachmentShortInfoModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_slot_base_model import InstructorSlotBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.detachment.convert_slot_vehicle_model import ConvertSlotVehicleModel
from gui.impl.gen.view_models.views.lobby.detachment.instructors_and_skins_model import InstructorsAndSkinsModel

class ConvertWindowModel(NavigationViewModel):
    __slots__ = ('onSaveChanges', 'onCancelChanges', 'onGoToAboutConvert', 'onCloseWindow')

    def __init__(self, properties=11, commands=7):
        super(ConvertWindowModel, self).__init__(properties=properties, commands=commands)

    @property
    def detachment(self):
        return self._getViewModel(2)

    @property
    def vehicle(self):
        return self._getViewModel(3)

    def getLeaderName(self):
        return self._getString(4)

    def setLeaderName(self, value):
        self._setString(4, value)

    def getCommanderRank(self):
        return self._getResource(5)

    def setCommanderRank(self, value):
        self._setResource(5, value)

    def getEliteTitle(self):
        return self._getResource(6)

    def setEliteTitle(self, value):
        self._setResource(6, value)

    def getAvailablePoints(self):
        return self._getNumber(7)

    def setAvailablePoints(self, value):
        self._setNumber(7, value)

    def getInstructors(self):
        return self._getArray(8)

    def setInstructors(self, value):
        self._setArray(8, value)

    def getInstructorsSlots(self):
        return self._getArray(9)

    def setInstructorsSlots(self, value):
        self._setArray(9, value)

    def getVehicleSlots(self):
        return self._getArray(10)

    def setVehicleSlots(self, value):
        self._setArray(10, value)

    def _initialize(self):
        super(ConvertWindowModel, self)._initialize()
        self._addViewModelProperty('detachment', DetachmentShortInfoModel())
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addStringProperty('leaderName', '')
        self._addResourceProperty('commanderRank', R.invalid())
        self._addResourceProperty('eliteTitle', R.invalid())
        self._addNumberProperty('availablePoints', 0)
        self._addArrayProperty('instructors', Array())
        self._addArrayProperty('instructorsSlots', Array())
        self._addArrayProperty('vehicleSlots', Array())
        self.onSaveChanges = self._addCommand('onSaveChanges')
        self.onCancelChanges = self._addCommand('onCancelChanges')
        self.onGoToAboutConvert = self._addCommand('onGoToAboutConvert')
        self.onCloseWindow = self._addCommand('onCloseWindow')
