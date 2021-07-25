# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/confirm_instructor_nation_change_view_model.py
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class ConfirmInstructorNationChangeViewModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=3):
        super(ConfirmInstructorNationChangeViewModel, self).__init__(properties=properties, commands=commands)

    def getNation(self):
        return self._getString(11)

    def setNation(self, value):
        self._setString(11, value)

    def getNewNation(self):
        return self._getString(12)

    def setNewNation(self, value):
        self._setString(12, value)

    def getTankmanName(self):
        return self._getString(13)

    def setTankmanName(self, value):
        self._setString(13, value)

    def _initialize(self):
        super(ConfirmInstructorNationChangeViewModel, self)._initialize()
        self._addStringProperty('nation', '')
        self._addStringProperty('newNation', '')
        self._addStringProperty('tankmanName', '')
