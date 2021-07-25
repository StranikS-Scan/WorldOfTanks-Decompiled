# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/recover_instructor_dialog_view_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class RecoverInstructorDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=3):
        super(RecoverInstructorDialogViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def priceModel(self):
        return self._getViewModel(11)

    def getBackground(self):
        return self._getResource(12)

    def setBackground(self, value):
        self._setResource(12, value)

    def getIcon(self):
        return self._getString(13)

    def setIcon(self, value):
        self._setString(13, value)

    def getNation(self):
        return self._getString(14)

    def setNation(self, value):
        self._setString(14, value)

    def getIsInBarracks(self):
        return self._getBool(15)

    def setIsInBarracks(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(RecoverInstructorDialogViewModel, self)._initialize()
        self._addViewModelProperty('priceModel', PriceModel())
        self._addResourceProperty('background', R.invalid())
        self._addStringProperty('icon', '')
        self._addStringProperty('nation', '')
        self._addBoolProperty('isInBarracks', False)
