# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/widgets/equipment_group_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.equipment_slot_model import EquipmentSlotModel

class EquipmentGroupModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(EquipmentGroupModel, self).__init__(properties=properties, commands=commands)

    @property
    def group(self):
        return self._getViewModel(0)

    @staticmethod
    def getGroupType():
        return EquipmentSlotModel

    def _initialize(self):
        super(EquipmentGroupModel, self)._initialize()
        self._addViewModelProperty('group', UserListModel())
