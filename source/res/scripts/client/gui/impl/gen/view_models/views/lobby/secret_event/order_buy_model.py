# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/order_buy_model.py
from gui.impl.gen import R
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.secret_event.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.secret_event.reward_model import RewardModel
from gui.impl.gen.view_models.views.lobby.secret_event.simple_general_model import SimpleGeneralModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class OrderBuyModel(FullScreenDialogWindowModel):
    __slots__ = ()
    SIMPLE = 'simple'
    PRIZE = 'prize'
    MEGAPACK = 'megapack'

    def __init__(self, properties=16, commands=2):
        super(OrderBuyModel, self).__init__(properties=properties, commands=commands)

    @property
    def orderPrice(self):
        return self._getViewModel(10)

    @property
    def orderList(self):
        return self._getViewModel(11)

    @property
    def rewardList(self):
        return self._getViewModel(12)

    @property
    def generalList(self):
        return self._getViewModel(13)

    def getGeneralIcon(self):
        return self._getResource(14)

    def setGeneralIcon(self, value):
        self._setResource(14, value)

    def getDialogType(self):
        return self._getString(15)

    def setDialogType(self, value):
        self._setString(15, value)

    def _initialize(self):
        super(OrderBuyModel, self)._initialize()
        self._addViewModelProperty('orderPrice', PriceModel())
        self._addViewModelProperty('orderList', UserListModel())
        self._addViewModelProperty('rewardList', UserListModel())
        self._addViewModelProperty('generalList', UserListModel())
        self._addResourceProperty('generalIcon', R.invalid())
        self._addStringProperty('dialogType', '')
