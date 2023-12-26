# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_toy_slots_bar_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.group_slots_model import GroupSlotsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.toys_list_model import ToysListModel

class NyToySlotsBarModel(ViewModel):
    __slots__ = ('onHoverSlot', 'onHoverOutSlot', 'onSelectSlot', 'onAnimationEnd')

    def __init__(self, properties=4, commands=4):
        super(NyToySlotsBarModel, self).__init__(properties=properties, commands=commands)

    @property
    def groupSlots(self):
        return self._getViewModel(0)

    @staticmethod
    def getGroupSlotsType():
        return GroupSlotsModel

    @property
    def toysList(self):
        return self._getViewModel(1)

    @staticmethod
    def getToysListType():
        return ToysListModel

    def getSelectedSlot(self):
        return self._getNumber(2)

    def setSelectedSlot(self, value):
        self._setNumber(2, value)

    def getHasNewToysAnimation(self):
        return self._getBool(3)

    def setHasNewToysAnimation(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(NyToySlotsBarModel, self)._initialize()
        self._addViewModelProperty('groupSlots', UserListModel())
        self._addViewModelProperty('toysList', ToysListModel())
        self._addNumberProperty('selectedSlot', -1)
        self._addBoolProperty('hasNewToysAnimation', False)
        self.onHoverSlot = self._addCommand('onHoverSlot')
        self.onHoverOutSlot = self._addCommand('onHoverOutSlot')
        self.onSelectSlot = self._addCommand('onSelectSlot')
        self.onAnimationEnd = self._addCommand('onAnimationEnd')
