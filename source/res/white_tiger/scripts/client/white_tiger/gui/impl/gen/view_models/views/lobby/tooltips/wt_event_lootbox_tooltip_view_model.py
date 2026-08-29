# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tooltips/wt_event_lootbox_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class WtEventLootboxTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(WtEventLootboxTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getIsHunterLootBox(self):
        return self._getBool(0)

    def setIsHunterLootBox(self, value):
        self._setBool(0, value)

    def getVehicleNames(self):
        return self._getArray(1)

    def setVehicleNames(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehicleNamesType():
        return unicode

    def getBonuses(self):
        return self._getArray(2)

    def setBonuses(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBonusesType():
        return IconBonusModel

    def _initialize(self):
        super(WtEventLootboxTooltipViewModel, self)._initialize()
        self._addBoolProperty('isHunterLootBox', False)
        self._addArrayProperty('vehicleNames', Array())
        self._addArrayProperty('bonuses', Array())
