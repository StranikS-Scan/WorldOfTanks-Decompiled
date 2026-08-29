# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_carousel_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_carousel_tank_model import WtCarouselTankModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_carousel_tank_status_model import WtCarouselTankStatusModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_equipment_group_model import WtEquipmentGroupModel

class WtCarouselViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(WtCarouselViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def status(self):
        return self._getViewModel(0)

    @staticmethod
    def getStatusType():
        return WtCarouselTankStatusModel

    def getIsDisableAll(self):
        return self._getBool(1)

    def setIsDisableAll(self, value):
        self._setBool(1, value)

    def getTanks(self):
        return self._getArray(2)

    def setTanks(self, value):
        self._setArray(2, value)

    @staticmethod
    def getTanksType():
        return WtCarouselTankModel

    def getEquipmentGroups(self):
        return self._getArray(3)

    def setEquipmentGroups(self, value):
        self._setArray(3, value)

    @staticmethod
    def getEquipmentGroupsType():
        return WtEquipmentGroupModel

    def _initialize(self):
        super(WtCarouselViewModel, self)._initialize()
        self._addViewModelProperty('status', WtCarouselTankStatusModel())
        self._addBoolProperty('isDisableAll', False)
        self._addArrayProperty('tanks', Array())
        self._addArrayProperty('equipmentGroups', Array())
        self.onClick = self._addCommand('onClick')
