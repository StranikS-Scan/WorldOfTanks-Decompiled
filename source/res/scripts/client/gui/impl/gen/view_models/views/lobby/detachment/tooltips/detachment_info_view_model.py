# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/detachment_info_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_top_panel_model import DetachmentTopPanelModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.demobilize_model import DemobilizeModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.detachment_info_slot_model import DetachmentInfoSlotModel

class DetachmentInfoViewModel(DetachmentTopPanelModel):
    __slots__ = ()

    def __init__(self, properties=20, commands=0):
        super(DetachmentInfoViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def demobilizeInfo(self):
        return self._getViewModel(13)

    def getDetachmentStatus(self):
        return self._getString(14)

    def setDetachmentStatus(self, value):
        self._setString(14, value)

    def getOpenInstSlotsCount(self):
        return self._getNumber(15)

    def setOpenInstSlotsCount(self, value):
        self._setNumber(15, value)

    def getIsDetachmentExists(self):
        return self._getBool(16)

    def setIsDetachmentExists(self, value):
        self._setBool(16, value)

    def getIsRecruitersExists(self):
        return self._getBool(17)

    def setIsRecruitersExists(self, value):
        self._setBool(17, value)

    def getVehicleSlots(self):
        return self._getArray(18)

    def setVehicleSlots(self, value):
        self._setArray(18, value)

    def getInstructorSlots(self):
        return self._getArray(19)

    def setInstructorSlots(self, value):
        self._setArray(19, value)

    def _initialize(self):
        super(DetachmentInfoViewModel, self)._initialize()
        self._addViewModelProperty('demobilizeInfo', DemobilizeModel())
        self._addStringProperty('detachmentStatus', '')
        self._addNumberProperty('openInstSlotsCount', 0)
        self._addBoolProperty('isDetachmentExists', False)
        self._addBoolProperty('isRecruitersExists', False)
        self._addArrayProperty('vehicleSlots', Array())
        self._addArrayProperty('instructorSlots', Array())
