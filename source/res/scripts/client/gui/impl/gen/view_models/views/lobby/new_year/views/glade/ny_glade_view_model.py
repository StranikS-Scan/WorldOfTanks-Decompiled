# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/ny_glade_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_entry_point_model import LootBoxEntryPointModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.atmosphere_animation_model import AtmosphereAnimationModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.group_slots_model import GroupSlotsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.ny_intro_model import NyIntroModel

class NyGladeViewModel(ViewModel):
    __slots__ = ('onHoverSlot', 'onHoverOutSlot', 'onMouseOver3dScene', 'onMoveSpace')

    def __init__(self, properties=5, commands=4):
        super(NyGladeViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def groupSlots(self):
        return self._getViewModel(0)

    @property
    def lootBox(self):
        return self._getViewModel(1)

    @property
    def intro(self):
        return self._getViewModel(2)

    @property
    def atmosphereAnimation(self):
        return self._getViewModel(3)

    def getIsIntroOpened(self):
        return self._getBool(4)

    def setIsIntroOpened(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(NyGladeViewModel, self)._initialize()
        self._addViewModelProperty('groupSlots', UserListModel())
        self._addViewModelProperty('lootBox', LootBoxEntryPointModel())
        self._addViewModelProperty('intro', NyIntroModel())
        self._addViewModelProperty('atmosphereAnimation', AtmosphereAnimationModel())
        self._addBoolProperty('isIntroOpened', False)
        self.onHoverSlot = self._addCommand('onHoverSlot')
        self.onHoverOutSlot = self._addCommand('onHoverOutSlot')
        self.onMouseOver3dScene = self._addCommand('onMouseOver3dScene')
        self.onMoveSpace = self._addCommand('onMoveSpace')
