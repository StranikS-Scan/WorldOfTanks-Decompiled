# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/pet/ny_pet_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.group_slots_model import GroupSlotsModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.loot_box_entry_point_model import LootBoxEntryPointModel

class NyPetModel(ViewModel):
    __slots__ = ('onLootBoxEntryPointClick', 'onMouseOver3dScene', 'onMoveSpace')

    def __init__(self, properties=4, commands=3):
        super(NyPetModel, self).__init__(properties=properties, commands=commands)

    @property
    def groupSlots(self):
        return self._getViewModel(0)

    @staticmethod
    def getGroupSlotsType():
        return GroupSlotsModel

    @property
    def lootBox(self):
        return self._getViewModel(1)

    @staticmethod
    def getLootBoxType():
        return LootBoxEntryPointModel

    def getIsSlotVisited(self):
        return self._getBool(2)

    def setIsSlotVisited(self, value):
        self._setBool(2, value)

    def getIsGuiLootBoxesVisible(self):
        return self._getBool(3)

    def setIsGuiLootBoxesVisible(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(NyPetModel, self)._initialize()
        self._addViewModelProperty('groupSlots', UserListModel())
        self._addViewModelProperty('lootBox', LootBoxEntryPointModel())
        self._addBoolProperty('isSlotVisited', False)
        self._addBoolProperty('isGuiLootBoxesVisible', False)
        self.onLootBoxEntryPointClick = self._addCommand('onLootBoxEntryPointClick')
        self.onMouseOver3dScene = self._addCommand('onMouseOver3dScene')
        self.onMoveSpace = self._addCommand('onMoveSpace')
