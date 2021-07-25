# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/new_commander_dialog_view_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.change_commander_dialog_view_model import ChangeCommanderDialogViewModel

class NewCommanderDialogViewModel(ChangeCommanderDialogViewModel):
    __slots__ = ('onBack',)

    def __init__(self, properties=19, commands=4):
        super(NewCommanderDialogViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(17)

    def getIsDetachmentLinked(self):
        return self._getBool(18)

    def setIsDetachmentLinked(self, value):
        self._setBool(18, value)

    def _initialize(self):
        super(NewCommanderDialogViewModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addBoolProperty('isDetachmentLinked', False)
        self.onBack = self._addCommand('onBack')
