# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/select_demount_kit_view_model.py
from gui.impl.gen.view_models.views.dialogs.sub_views.select_option_base_item_view_model import SelectOptionBaseItemViewModel

class SelectDemountKitViewModel(SelectOptionBaseItemViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(SelectDemountKitViewModel, self).__init__(properties=properties, commands=commands)

    def getStorageCount(self):
        return self._getNumber(4)

    def setStorageCount(self, value):
        self._setNumber(4, value)

    def getText(self):
        return self._getString(5)

    def setText(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(SelectDemountKitViewModel, self)._initialize()
        self._addNumberProperty('storageCount', 0)
        self._addStringProperty('text', '')
