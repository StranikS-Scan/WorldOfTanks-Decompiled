# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/demount_instructor_dialog_view_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel
from gui.impl.gen.view_models.windows.selector_dialog_model import SelectorDialogModel

class DemountInstructorDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ()
    WAIT = 'wait'
    GOLD = 'gold'

    def __init__(self, properties=18, commands=3):
        super(DemountInstructorDialogViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def selector(self):
        return self._getViewModel(11)

    def getBackground(self):
        return self._getResource(12)

    def setBackground(self, value):
        self._setResource(12, value)

    def getName(self):
        return self._getString(13)

    def setName(self, value):
        self._setString(13, value)

    def getIcon(self):
        return self._getString(14)

    def setIcon(self, value):
        self._setString(14, value)

    def getNation(self):
        return self._getString(15)

    def setNation(self, value):
        self._setString(15, value)

    def getAvailableAfterDays(self):
        return self._getNumber(16)

    def setAvailableAfterDays(self, value):
        self._setNumber(16, value)

    def getIsInOtherDetachment(self):
        return self._getBool(17)

    def setIsInOtherDetachment(self, value):
        self._setBool(17, value)

    def _initialize(self):
        super(DemountInstructorDialogViewModel, self)._initialize()
        self._addViewModelProperty('selector', SelectorDialogModel())
        self._addResourceProperty('background', R.invalid())
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('nation', '')
        self._addNumberProperty('availableAfterDays', 0)
        self._addBoolProperty('isInOtherDetachment', False)
