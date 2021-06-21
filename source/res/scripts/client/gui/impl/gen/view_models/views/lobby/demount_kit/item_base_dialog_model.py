# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/demount_kit/item_base_dialog_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class ItemBaseDialogModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=3):
        super(ItemBaseDialogModel, self).__init__(properties=properties, commands=commands)

    def getImage(self):
        return self._getResource(10)

    def setImage(self, value):
        self._setResource(10, value)

    def getDescription(self):
        return self._getResource(11)

    def setDescription(self, value):
        self._setResource(11, value)

    def getSpecialType(self):
        return self._getString(12)

    def setSpecialType(self, value):
        self._setString(12, value)

    def _initialize(self):
        super(ItemBaseDialogModel, self)._initialize()
        self._addResourceProperty('image', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addStringProperty('specialType', '')
