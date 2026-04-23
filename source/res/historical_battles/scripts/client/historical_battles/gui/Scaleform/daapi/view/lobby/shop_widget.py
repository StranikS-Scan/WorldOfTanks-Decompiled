# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/shop_widget.py
import HBAccountSettings
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from helpers.CallbackDelayer import CallbackDelayer
from historical_battles.gui.shared.event_dispatcher import showShopView
from historical_battles_common.hb_constants import AccountSettingsKeys
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_widget_model import ShopWidgetModel
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from gui.impl.pub import ViewImpl

class ShopWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return ShopWidgetView(R.views.historical_battles.lobby.ShopWidget())


class ShopWidgetView(ViewImpl):
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = ShopWidgetModel()
        super(ShopWidgetView, self).__init__(settings)
        self.__tooltipEnabled = True
        self.__callbackDelayer = CallbackDelayer()

    @property
    def viewModel(self):
        return super(ShopWidgetView, self).getViewModel()

    def _getEvents(self):
        return ((self.__gameEventController.frontDataUpdated, self.__onFrontDataUpdated),)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            specialArgs = []
            window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs), self.getParentWindow())
            window.load()
            return window
        return super(ShopWidgetView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return None if not self.__tooltipEnabled else super(ShopWidgetView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(ShopWidgetView, self)._onLoading(*args, **kwargs)
        self.__setFrontType()
        self.viewModel.onClick += self.__onClick

    def __setFrontType(self):
        currentFront = self.__gameEventController.frontController.getSelectedFront()
        with self.viewModel.transaction() as model:
            model.setFrontType(currentFront.getName())

    def __onFrontDataUpdated(self, *_):
        self.__setFrontType()

    def _finalize(self):
        self.viewModel.onClick -= self.__onClick
        super(ShopWidgetView, self)._finalize()

    def __onClick(self):
        HBAccountSettings.setNotifications(AccountSettingsKeys.SEEN_HISTORICAL_BATTLES_SHOP, True)
        showShopView()
