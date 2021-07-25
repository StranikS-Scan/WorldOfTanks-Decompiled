# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/personal_case_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_top_panel_model import DetachmentTopPanelModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_short_model import PerkShortModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.detachment.personal_case.instructor_slot_model import InstructorSlotModel
from gui.impl.gen.view_models.views.lobby.detachment.personal_case.vehicle_slot_model import VehicleSlotModel

class PersonalCaseModel(NavigationViewModel):
    __slots__ = ('onVehicleSlotClick', 'onInstructorClick', 'onInstructorDemountClick', 'onInstructorsPreviewClick', 'onDemountInstructorClick', 'onDemobilizeDetachmentClick', 'onPerksPreviewClick')

    def __init__(self, properties=13, commands=10):
        super(PersonalCaseModel, self).__init__(properties=properties, commands=commands)

    @property
    def topPanelModel(self):
        return self._getViewModel(2)

    @property
    def currentVehicle(self):
        return self._getViewModel(3)

    def getNewSkinsCount(self):
        return self._getNumber(4)

    def setNewSkinsCount(self, value):
        self._setNumber(4, value)

    def getNewAllowanceCount(self):
        return self._getNumber(5)

    def setNewAllowanceCount(self, value):
        self._setNumber(5, value)

    def getIsInstPreviewAvailable(self):
        return self._getBool(6)

    def setIsInstPreviewAvailable(self, value):
        self._setBool(6, value)

    def getIsDismissDisable(self):
        return self._getBool(7)

    def setIsDismissDisable(self, value):
        self._setBool(7, value)

    def getCanCustomizeCommander(self):
        return self._getBool(8)

    def setCanCustomizeCommander(self, value):
        self._setBool(8, value)

    def getHasVehicleLock(self):
        return self._getBool(9)

    def setHasVehicleLock(self, value):
        self._setBool(9, value)

    def getVehicleSlots(self):
        return self._getArray(10)

    def setVehicleSlots(self, value):
        self._setArray(10, value)

    def getInstructorSlots(self):
        return self._getArray(11)

    def setInstructorSlots(self, value):
        self._setArray(11, value)

    def getPerks(self):
        return self._getArray(12)

    def setPerks(self, value):
        self._setArray(12, value)

    def _initialize(self):
        super(PersonalCaseModel, self)._initialize()
        self._addViewModelProperty('topPanelModel', DetachmentTopPanelModel())
        self._addViewModelProperty('currentVehicle', VehicleModel())
        self._addNumberProperty('newSkinsCount', 0)
        self._addNumberProperty('newAllowanceCount', 0)
        self._addBoolProperty('isInstPreviewAvailable', False)
        self._addBoolProperty('isDismissDisable', False)
        self._addBoolProperty('canCustomizeCommander', False)
        self._addBoolProperty('hasVehicleLock', False)
        self._addArrayProperty('vehicleSlots', Array())
        self._addArrayProperty('instructorSlots', Array())
        self._addArrayProperty('perks', Array())
        self.onVehicleSlotClick = self._addCommand('onVehicleSlotClick')
        self.onInstructorClick = self._addCommand('onInstructorClick')
        self.onInstructorDemountClick = self._addCommand('onInstructorDemountClick')
        self.onInstructorsPreviewClick = self._addCommand('onInstructorsPreviewClick')
        self.onDemountInstructorClick = self._addCommand('onDemountInstructorClick')
        self.onDemobilizeDetachmentClick = self._addCommand('onDemobilizeDetachmentClick')
        self.onPerksPreviewClick = self._addCommand('onPerksPreviewClick')
