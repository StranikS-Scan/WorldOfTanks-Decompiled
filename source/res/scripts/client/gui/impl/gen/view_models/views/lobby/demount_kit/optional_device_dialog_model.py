# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/demount_kit/optional_device_dialog_model.py
from gui.impl.gen.view_models.views.lobby.demount_kit.item_price_dialog_model import ItemPriceDialogModel

class OptionalDeviceDialogModel(ItemPriceDialogModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=3):
        super(OptionalDeviceDialogModel, self).__init__(properties=properties, commands=commands)

    def getSpecialType(self):
        return self._getString(17)

    def setSpecialType(self, value):
        self._setString(17, value)

    def _initialize(self):
        super(OptionalDeviceDialogModel, self)._initialize()
        self._addStringProperty('specialType', '')
