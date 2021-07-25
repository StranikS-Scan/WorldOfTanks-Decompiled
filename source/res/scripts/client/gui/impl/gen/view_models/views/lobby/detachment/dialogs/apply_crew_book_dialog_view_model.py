# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/apply_crew_book_dialog_view_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_top_panel_model import DetachmentTopPanelModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class ApplyCrewBookDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ('onStepperChange',)

    def __init__(self, properties=20, commands=4):
        super(ApplyCrewBookDialogViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def topPanelModel(self):
        return self._getViewModel(11)

    def getNation(self):
        return self._getString(12)

    def setNation(self, value):
        self._setString(12, value)

    def getVehicleName(self):
        return self._getString(13)

    def setVehicleName(self, value):
        self._setString(13, value)

    def getCrewBookType(self):
        return self._getString(14)

    def setCrewBookType(self, value):
        self._setString(14, value)

    def getAmountXP(self):
        return self._getNumber(15)

    def setAmountXP(self, value):
        self._setNumber(15, value)

    def getMaxValue(self):
        return self._getNumber(16)

    def setMaxValue(self, value):
        self._setNumber(16, value)

    def getSelectedValue(self):
        return self._getNumber(17)

    def setSelectedValue(self, value):
        self._setNumber(17, value)

    def getIsMaxLevel(self):
        return self._getBool(18)

    def setIsMaxLevel(self, value):
        self._setBool(18, value)

    def getAmountXPAfterElite(self):
        return self._getNumber(19)

    def setAmountXPAfterElite(self, value):
        self._setNumber(19, value)

    def _initialize(self):
        super(ApplyCrewBookDialogViewModel, self)._initialize()
        self._addViewModelProperty('topPanelModel', DetachmentTopPanelModel())
        self._addStringProperty('nation', '')
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('crewBookType', '')
        self._addNumberProperty('amountXP', 0)
        self._addNumberProperty('maxValue', 1)
        self._addNumberProperty('selectedValue', 1)
        self._addBoolProperty('isMaxLevel', False)
        self._addNumberProperty('amountXPAfterElite', 0)
        self.onStepperChange = self._addCommand('onStepperChange')
