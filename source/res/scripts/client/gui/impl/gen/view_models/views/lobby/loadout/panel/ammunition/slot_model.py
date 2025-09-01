# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/loadout/panel/ammunition/slot_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.loadout.panel.ammunition.specialization import Specialization

class SlotModel(ViewModel):
    __slots__ = ()
    CONSUMABLE_ITEM_TYPE = 'consumable'
    SHELL_ITEM_TYPE = 'shell'
    EQUIPMENT_ITEM_TYPE = 'equipment'
    INSTRUCTION_ITEM_TYPE = 'instruction'

    def __init__(self, properties=5, commands=0):
        super(SlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def specialization(self):
        return self._getViewModel(0)

    @staticmethod
    def getSpecializationType():
        return Specialization

    def getId(self):
        return self._getString(1)

    def setId(self, value):
        self._setString(1, value)

    def getItemId(self):
        return self._getString(2)

    def setItemId(self, value):
        self._setString(2, value)

    def getItemType(self):
        return self._getString(3)

    def setItemType(self, value):
        self._setString(3, value)

    def getBindedKey(self):
        return self._getString(4)

    def setBindedKey(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(SlotModel, self)._initialize()
        self._addViewModelProperty('specialization', Specialization())
        self._addStringProperty('id', '')
        self._addStringProperty('itemId', '')
        self._addStringProperty('itemType', '')
        self._addStringProperty('bindedKey', '')
