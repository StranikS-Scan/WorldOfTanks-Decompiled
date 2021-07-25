# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/detachment_info_tooltip_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_top_panel_model import DetachmentTopPanelModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.demobilize_model import DemobilizeModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.detachment_info_instructor_model import DetachmentInfoInstructorModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.detachment_info_slot_model import DetachmentInfoSlotModel

class DetachmentInfoTooltipModel(DetachmentTopPanelModel):
    __slots__ = ()

    def __init__(self, properties=23, commands=0):
        super(DetachmentInfoTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def demobilizeInfo(self):
        return self._getViewModel(13)

    def getLockState(self):
        return self._getString(14)

    def setLockState(self, value):
        self._setString(14, value)

    def getOpenInstSlotsCount(self):
        return self._getNumber(15)

    def setOpenInstSlotsCount(self, value):
        self._setNumber(15, value)

    def getIsDismissed(self):
        return self._getBool(16)

    def setIsDismissed(self, value):
        self._setBool(16, value)

    def getHasLockCrew(self):
        return self._getBool(17)

    def setHasLockCrew(self, value):
        self._setBool(17, value)

    def getIsDetachmentExists(self):
        return self._getBool(18)

    def setIsDetachmentExists(self, value):
        self._setBool(18, value)

    def getIsRecruitersExists(self):
        return self._getBool(19)

    def setIsRecruitersExists(self, value):
        self._setBool(19, value)

    def getHasInstructors(self):
        return self._getBool(20)

    def setHasInstructors(self, value):
        self._setBool(20, value)

    def getVehicleSlots(self):
        return self._getArray(21)

    def setVehicleSlots(self, value):
        self._setArray(21, value)

    def getInstructorSlots(self):
        return self._getArray(22)

    def setInstructorSlots(self, value):
        self._setArray(22, value)

    def _initialize(self):
        super(DetachmentInfoTooltipModel, self)._initialize()
        self._addViewModelProperty('demobilizeInfo', DemobilizeModel())
        self._addStringProperty('lockState', '')
        self._addNumberProperty('openInstSlotsCount', 0)
        self._addBoolProperty('isDismissed', False)
        self._addBoolProperty('hasLockCrew', False)
        self._addBoolProperty('isDetachmentExists', False)
        self._addBoolProperty('isRecruitersExists', False)
        self._addBoolProperty('hasInstructors', False)
        self._addArrayProperty('vehicleSlots', Array())
        self._addArrayProperty('instructorSlots', Array())
