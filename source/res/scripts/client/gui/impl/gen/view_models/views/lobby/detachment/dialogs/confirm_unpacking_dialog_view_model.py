# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/confirm_unpacking_dialog_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_base_model import PerkBaseModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class ConfirmUnpackingDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=3):
        super(ConfirmUnpackingDialogViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def additionalPerk(self):
        return self._getViewModel(11)

    def getIcon(self):
        return self._getString(12)

    def setIcon(self, value):
        self._setString(12, value)

    def getNation(self):
        return self._getString(13)

    def setNation(self, value):
        self._setString(13, value)

    def getName(self):
        return self._getString(14)

    def setName(self, value):
        self._setString(14, value)

    def getBackground(self):
        return self._getResource(15)

    def setBackground(self, value):
        self._setResource(15, value)

    def getPerks(self):
        return self._getArray(16)

    def setPerks(self, value):
        self._setArray(16, value)

    def getCanApply(self):
        return self._getBool(17)

    def setCanApply(self, value):
        self._setBool(17, value)

    def getNotEnoughSlots(self):
        return self._getBool(18)

    def setNotEnoughSlots(self, value):
        self._setBool(18, value)

    def _initialize(self):
        super(ConfirmUnpackingDialogViewModel, self)._initialize()
        self._addViewModelProperty('additionalPerk', PerkBaseModel())
        self._addStringProperty('icon', '')
        self._addStringProperty('nation', '')
        self._addStringProperty('name', '')
        self._addResourceProperty('background', R.invalid())
        self._addArrayProperty('perks', Array())
        self._addBoolProperty('canApply', False)
        self._addBoolProperty('notEnoughSlots', False)
