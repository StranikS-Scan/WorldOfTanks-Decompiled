# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_carousel_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_carousel_tank_model import WtCarouselTankModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_carousel_tank_status_model import WtCarouselTankStatusModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_equipment_group_model import WtEquipmentGroupModel

class WtCarouselViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(WtCarouselViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def tanks(self):
        return self._getViewModel(0)

    @staticmethod
    def getTanksType():
        return WtCarouselTankModel

    @property
    def status(self):
        return self._getViewModel(1)

    @staticmethod
    def getStatusType():
        return WtCarouselTankStatusModel

    @property
    def equipment(self):
        return self._getViewModel(2)

    @staticmethod
    def getEquipmentType():
        return WtEquipmentGroupModel

    def getIsDisableAll(self):
        return self._getBool(3)

    def setIsDisableAll(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(WtCarouselViewModel, self)._initialize()
        self._addViewModelProperty('tanks', UserListModel())
        self._addViewModelProperty('status', WtCarouselTankStatusModel())
        self._addViewModelProperty('equipment', UserListModel())
        self._addBoolProperty('isDisableAll', False)
        self.onClick = self._addCommand('onClick')
