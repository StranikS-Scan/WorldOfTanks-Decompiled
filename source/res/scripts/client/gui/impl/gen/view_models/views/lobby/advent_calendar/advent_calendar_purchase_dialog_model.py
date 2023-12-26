# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/advent_calendar/advent_calendar_purchase_dialog_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.advent_calendar.components.advent_calendar_ny_kit_model import AdventCalendarNyKitModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resources_balance_model import NyResourcesBalanceModel

class AdventCalendarPurchaseDialogModel(ViewModel):
    __slots__ = ('onAccept', 'onCancel', 'onSwithToBoxes')

    def __init__(self, properties=4, commands=3):
        super(AdventCalendarPurchaseDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def balance(self):
        return self._getViewModel(0)

    @staticmethod
    def getBalanceType():
        return NyResourcesBalanceModel

    @property
    def resources(self):
        return self._getViewModel(1)

    @staticmethod
    def getResourcesType():
        return AdventCalendarNyKitModel

    def getDayId(self):
        return self._getNumber(2)

    def setDayId(self, value):
        self._setNumber(2, value)

    def getIsWalletAvailable(self):
        return self._getBool(3)

    def setIsWalletAvailable(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(AdventCalendarPurchaseDialogModel, self)._initialize()
        self._addViewModelProperty('balance', NyResourcesBalanceModel())
        self._addViewModelProperty('resources', AdventCalendarNyKitModel())
        self._addNumberProperty('dayId', 0)
        self._addBoolProperty('isWalletAvailable', True)
        self.onAccept = self._addCommand('onAccept')
        self.onCancel = self._addCommand('onCancel')
        self.onSwithToBoxes = self._addCommand('onSwithToBoxes')
