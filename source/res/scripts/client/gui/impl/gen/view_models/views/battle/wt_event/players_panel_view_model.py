# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/wt_event/players_panel_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tooltips.vehicle_item_model import VehicleItemModel

class PlayersPanelViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PlayersPanelViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rightList(self):
        return self._getViewModel(0)

    @property
    def leftList(self):
        return self._getViewModel(1)

    def getTitle(self):
        return self._getString(2)

    def setTitle(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(PlayersPanelViewModel, self)._initialize()
        self._addViewModelProperty('rightList', UserListModel())
        self._addViewModelProperty('leftList', UserListModel())
        self._addStringProperty('title', '')
