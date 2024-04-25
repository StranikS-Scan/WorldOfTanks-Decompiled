# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hangar_view_model.py
from frameworks.wulf import Array
from historical_battles.gui.impl.gen.view_models.views.common.selectable_view_model import SelectableViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.base_frontman_model import BaseFrontmanModel
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_mode_widget_model import BattleModeWidgetModel
from historical_battles.gui.impl.gen.view_models.views.lobby.orders_model import OrdersModel
from historical_battles.gui.impl.gen.view_models.views.lobby.progression_button_model import ProgressionButtonModel
from historical_battles.gui.impl.gen.view_models.views.lobby.quest_progresive_model import QuestProgresiveModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_button_model import ShopButtonModel

class HangarViewModel(SelectableViewModel):
    __slots__ = ('onFrontmanChanged', 'onEscapePressed', 'onInfoClick', 'onCloseClick', 'onMousePressed', 'onVehicleChange')

    def __init__(self, properties=8, commands=8):
        super(HangarViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def orders(self):
        return self._getViewModel(0)

    @staticmethod
    def getOrdersType():
        return OrdersModel

    @property
    def shopButton(self):
        return self._getViewModel(1)

    @staticmethod
    def getShopButtonType():
        return ShopButtonModel

    @property
    def progressionButton(self):
        return self._getViewModel(2)

    @staticmethod
    def getProgressionButtonType():
        return ProgressionButtonModel

    @property
    def battleModeWidget(self):
        return self._getViewModel(3)

    @staticmethod
    def getBattleModeWidgetType():
        return BattleModeWidgetModel

    @property
    def progress(self):
        return self._getViewModel(4)

    @staticmethod
    def getProgressType():
        return QuestProgresiveModel

    def getFrontmen(self):
        return self._getArray(5)

    def setFrontmen(self, value):
        self._setArray(5, value)

    @staticmethod
    def getFrontmenType():
        return BaseFrontmanModel

    def getBanExpirationTime(self):
        return self._getNumber(6)

    def setBanExpirationTime(self, value):
        self._setNumber(6, value)

    def getSelectedFrontmanId(self):
        return self._getNumber(7)

    def setSelectedFrontmanId(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(HangarViewModel, self)._initialize()
        self._addViewModelProperty('orders', OrdersModel())
        self._addViewModelProperty('shopButton', ShopButtonModel())
        self._addViewModelProperty('progressionButton', ProgressionButtonModel())
        self._addViewModelProperty('battleModeWidget', BattleModeWidgetModel())
        self._addViewModelProperty('progress', QuestProgresiveModel())
        self._addArrayProperty('frontmen', Array())
        self._addNumberProperty('banExpirationTime', 0)
        self._addNumberProperty('selectedFrontmanId', 0)
        self.onFrontmanChanged = self._addCommand('onFrontmanChanged')
        self.onEscapePressed = self._addCommand('onEscapePressed')
        self.onInfoClick = self._addCommand('onInfoClick')
        self.onCloseClick = self._addCommand('onCloseClick')
        self.onMousePressed = self._addCommand('onMousePressed')
        self.onVehicleChange = self._addCommand('onVehicleChange')
