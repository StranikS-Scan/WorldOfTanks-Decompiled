# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_group_slots_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_slot_model import NySlotModel

class NyGroupSlotsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NyGroupSlotsModel, self).__init__(properties=properties, commands=commands)

    @property
    def slots(self):
        return self._getViewModel(0)

    def _initialize(self):
        super(NyGroupSlotsModel, self)._initialize()
        self._addViewModelProperty('slots', UserListModel())
