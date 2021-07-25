# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/change_commander_dialog_view_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.ui_kit.gf_drop_down_model import GfDropDownModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class ChangeCommanderDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=3):
        super(ChangeCommanderDialogViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def names(self):
        return self._getViewModel(11)

    @property
    def surnames(self):
        return self._getViewModel(12)

    def getIconName(self):
        return self._getString(13)

    def setIconName(self, value):
        self._setString(13, value)

    def getName(self):
        return self._getString(14)

    def setName(self, value):
        self._setString(14, value)

    def getType(self):
        return self._getString(15)

    def setType(self, value):
        self._setString(15, value)

    def getDescription(self):
        return self._getResource(16)

    def setDescription(self, value):
        self._setResource(16, value)

    def _initialize(self):
        super(ChangeCommanderDialogViewModel, self)._initialize()
        self._addViewModelProperty('names', GfDropDownModel())
        self._addViewModelProperty('surnames', GfDropDownModel())
        self._addStringProperty('iconName', '')
        self._addStringProperty('name', '')
        self._addStringProperty('type', '')
        self._addResourceProperty('description', R.invalid())
