# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/sub_views/top_right/event_money_balance.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from helpers import dependency
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from skeletons.gui.game_event_controller import IGameEventController
from gui.impl.gen.view_models.views.dialogs.sub_views.event_money_balance_view_model import EventMoneyBalanceViewModel

class EventMoneyBalance(ViewImpl):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, layoutID=R.views.dialogs.sub_views.topRight.EventMoneyBalance()):
        settings = ViewSettings(layoutID)
        settings.model = EventMoneyBalanceViewModel()
        super(EventMoneyBalance, self).__init__(settings)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            window = BackportTooltipWindow(createTooltipData(tooltip='', isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EVENT_KEY_INFO, specialArgs=[]), self.getParentWindow())
            window.load()
            return window
        super(EventMoneyBalance, self).createToolTip(event)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EventMoneyBalance, self)._onLoading(*args, **kwargs)
        shop = self._gameEventController.getShop()
        shop.onBundleUnlocked += self.__onBundleUpdate
        self._gameEventController.onRewardBoxKeyUpdated += self.__setStats
        self.__setStats()

    def _finalize(self):
        shop = self._gameEventController.getShop()
        shop.onBundleUnlocked -= self.__onBundleUpdate
        self._gameEventController.onRewardBoxKeyUpdated -= self.__setStats
        super(EventMoneyBalance, self)._finalize()

    def __onBundleUpdate(self, _):
        self.__setStats()

    def __setStats(self):
        shop = self._gameEventController.getShop()
        self.viewModel.setKeyCount(shop.getKeys())
