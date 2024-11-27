# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/pet/ny_pet_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.group_slots_model import GroupSlotsModel

class NyPetModel(ViewModel):
    __slots__ = ('onMouseOver3dScene', 'onMoveSpace')

    def __init__(self, properties=2, commands=2):
        super(NyPetModel, self).__init__(properties=properties, commands=commands)

    @property
    def groupSlots(self):
        return self._getViewModel(0)

    @staticmethod
    def getGroupSlotsType():
        return GroupSlotsModel

    def getIsSlotVisited(self):
        return self._getBool(1)

    def setIsSlotVisited(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(NyPetModel, self)._initialize()
        self._addViewModelProperty('groupSlots', UserListModel())
        self._addBoolProperty('isSlotVisited', False)
        self.onMouseOver3dScene = self._addCommand('onMouseOver3dScene')
        self.onMoveSpace = self._addCommand('onMoveSpace')
