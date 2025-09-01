# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/widgets/hangar_consumables_panel_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen import R
from gui.impl.wrappers.user_list_model import UserListModel
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.equipment_group_model import EquipmentGroupModel

class TankTypeEnum(Enum):
    HUNTER = 'wt_hunter'
    BOSS = 'wt_boss'
    SPECIALBOSS = 'wt_special_boss'


class HangarConsumablesPanelViewModel(ViewModel):
    __slots__ = ('onOpenTasks', 'onBuyTicket')

    def __init__(self, properties=5, commands=2):
        super(HangarConsumablesPanelViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def equipments(self):
        return self._getViewModel(0)

    @staticmethod
    def getEquipmentsType():
        return EquipmentGroupModel

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getQuantity(self):
        return self._getNumber(3)

    def setQuantity(self, value):
        self._setNumber(3, value)

    def getTankType(self):
        return TankTypeEnum(self._getString(4))

    def setTankType(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(HangarConsumablesPanelViewModel, self)._initialize()
        self._addViewModelProperty('equipments', UserListModel())
        self._addStringProperty('title', '')
        self._addResourceProperty('icon', R.invalid())
        self._addNumberProperty('quantity', -1)
        self._addStringProperty('tankType')
        self.onOpenTasks = self._addCommand('onOpenTasks')
        self.onBuyTicket = self._addCommand('onBuyTicket')
