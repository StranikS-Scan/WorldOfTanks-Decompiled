# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/tooltips/test_drive_info_tooltip_view_model.py
from frameworks.wulf import ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.rent_price_model import RentPriceModel

class TestDriveInfoTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TestDriveInfoTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return RentPriceModel

    def getTestDriveDays(self):
        return self._getNumber(1)

    def setTestDriveDays(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(TestDriveInfoTooltipViewModel, self)._initialize()
        self._addViewModelProperty('price', RentPriceModel())
        self._addNumberProperty('testDriveDays', 0)
