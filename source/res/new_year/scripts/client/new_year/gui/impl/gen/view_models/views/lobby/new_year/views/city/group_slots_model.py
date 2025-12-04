# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/city/group_slots_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.slot_model import SlotModel

class GroupSlotsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(GroupSlotsModel, self).__init__(properties=properties, commands=commands)

    @property
    def slots(self):
        return self._getViewModel(0)

    @staticmethod
    def getSlotsType():
        return SlotModel

    def getHasToysHint(self):
        return self._getBool(1)

    def setHasToysHint(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(GroupSlotsModel, self)._initialize()
        self._addViewModelProperty('slots', UserListModel())
        self._addBoolProperty('hasToysHint', False)
