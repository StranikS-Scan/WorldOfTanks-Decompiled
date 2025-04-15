# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/division_confirm_upgrade_view.py
import BigWorld
from functools import partial
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl import backport
from historical_battles.gui.impl.gen.view_models.views.lobby.division_confirm_upgrade_view_model import DivisionConfirmUpgradeViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.shared.money import Currency
from helpers import dependency
from gui.ClientUpdateManager import g_clientUpdateManager
from historical_battles_common.hb_constants import HB_DIVISION_UPGRADE_OFFER_PARAMS_KEY
from historical_battles_common import account_commands
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from historical_battles.gui.impl.lobby.views.bonus_packer import getBonusPacker
from gui.server_events.bonuses import getNonQuestBonuses
from gui.impl.backport import BackportTooltipWindow
from historical_battles.gui.impl.lobby.tooltips.order_tooltip import OrderTooltip
from gui.impl.pub.tooltip_window import ToolTipWindow, SimpleTooltipContent
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.dialogs.dialog_template_utils import getCurrencyTooltipAlias
from gui.impl.dialogs.dialog_template_tooltip import DialogTemplateTooltip
from gui.impl.dialogs.sub_views.top_right.money_balance import NO_WGM_TOOLTIP_DATA
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.hb_tooltips_constants import HbTooltipsConstants
import logging
_logger = logging.getLogger(__name__)

class DivisionConfirmUpgradeView(ViewImpl):
    __gameEventController = dependency.descriptor(IGameEventController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ('__subdivisionId', '__tooltipItems', '__isMoneyBalanceAvailable', '__currencyTooltips')

    def __init__(self, layoutID, subdivisionId):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = DivisionConfirmUpgradeViewModel()
        super(DivisionConfirmUpgradeView, self).__init__(settings)
        self.__subdivisionId = subdivisionId
        self.__tooltipItems = {}
        self.__isMoneyBalanceAvailable = False
        self.__currencyTooltips = self.__defaultCurrenciesTooltips()

    @property
    def viewModel(self):
        return super(DivisionConfirmUpgradeView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onBuy, self.__onBuy), (self.viewModel.onClose, self.__onClose))

    def _getConfig(self):
        settings = self.__lobbyContext.getServerSettings().getSettings()
        return settings.get(HB_DIVISION_UPGRADE_OFFER_PARAMS_KEY, {})

    def _onLoading(self, *args, **kwargs):
        super(DivisionConfirmUpgradeView, self)._onLoading(*args, **kwargs)
        g_clientUpdateManager.addMoneyCallback(self.__moneyChangeHandler)
        self.__updateModel()

    def _finalize(self):
        self.__tooltipItems = None
        self.__subdivisionId = None
        self.__isMoneyBalanceAvailable = None
        self.__currencyTooltips = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(DivisionConfirmUpgradeView, self)._finalize()
        return

    def __updateModel(self):
        self.__tooltipItems = {}
        with self.viewModel.transaction() as model:
            currentFront = self.__gameEventController.frontController.getSelectedFront()
            model.setFrontName(currentFront.getName())
            model.setSubDivisionIndex(self.__subdivisionId)
            model.setIsEnoughMoney(self.__checkBalance())
            price = self.__getCurrentPrice()
            if not price or price < 0:
                _logger.warning('Invalid price. Price must be greater or equal than 0')
            else:
                model.setPrice(price)
            self.__setRewards(model)
            self.__setMoneyBalance(model)

    def __setRewards(self, model):
        data = self._getConfig().get('rewardsInfo', {})
        if not data:
            _logger.warning('No awardList section')
            return
        rewards = model.getRewards()
        rewards.clear()
        for bonus in data.get('bonuses', []):
            bonus = getNonQuestBonuses(bonus[0], bonus[1])
            packBonusModelAndTooltipData(bonus, rewards, self.__tooltipItems, getBonusPacker())

        rewards.invalidate()

    def __setMoneyBalance(self, model):
        stats = self.__itemsCache.items.stats
        self.__isMoneyBalanceAvailable = stats.mayConsumeWalletResources
        model.setIsMoneyBalanceAvailable(self.__isMoneyBalanceAvailable)
        if self.__isMoneyBalanceAvailable:
            model.setGold(int(stats.money.getSignValue(Currency.GOLD)))
            model.setFreeExp(stats.freeXP)
            model.setCredits(int(stats.money.getSignValue(Currency.CREDITS)))
            model.setCrystals(int(stats.money.getSignValue(Currency.CRYSTAL)))
        self.__fillCurrencyTooltipFactories()

    def __getCurrentPrice(self):
        config = self._getConfig()
        if not config or not config.get('price'):
            _logger.warning('Invalid division confirm upgrade config')
            return None
        else:
            return config.get('price')

    def __onBuy(self, *args):
        if not self.__isMoneyBalanceAvailable:
            _logger.error('Money balance is not available.')
            return
        if self.__checkBalance():
            callback = self.__onBuyCallback
            BigWorld.player()._doCmdInt(account_commands.CMD_HB_BUY_DIVISION_MAX_EXP, self.__subdivisionId, lambda requestID, resultID, errorCode, ext: callback(resultID, errorCode))

    def __onBuyCallback(self, resultID, errorCode):
        if errorCode:
            _logger.error('Transaction failed. Check BASE logs. Error code: %r, resultID = %r', errorCode, resultID)
        self.destroyWindow()

    def __checkBalance(self):
        price = self.__getCurrentPrice()
        stats = self.__itemsCache.items.stats
        return stats.mayConsumeWalletResources and price <= stats.money.getSignValue(Currency.GOLD)

    def __onClose(self, *args):
        self.destroyWindow()

    def __moneyChangeHandler(self, *_):
        self.__updateMoneyBalance()

    def __updateMoneyBalance(self):
        with self.viewModel.transaction() as model:
            self.__setMoneyBalance(model)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId', None)
            if not tooltipId:
                return
            tooltip = self.__tooltipItems.get(tooltipId, None)
            if tooltip:
                window = BackportTooltipWindow(tooltip, self.getParentWindow())
                window.load()
        elif event.contentID == R.views.historical_battles.lobby.tooltips.OrderTooltip():
            orderType = event.getArgument('tokenName').split('_')[-1]
            if not orderType:
                return
            content = OrderTooltip(orderType)
            window = ToolTipWindow(event, content, self.getParentWindow())
            window.load()
            window.move(event.mouse.positionX, event.mouse.positionY)
        elif event.contentID == R.views.dialogs.common.DialogTemplateGenericTooltip():
            tooltipId = event.getArgument('tooltipId')
            content = None
            if tooltipId == HbTooltipsConstants.TOOLTIP_NOT_ENOUGH_MONEY:
                content = createBackportTooltipContent(TOOLTIPS_CONSTANTS.NOT_ENOUGH_MONEY, (int(event.getArgument('value')), event.getArgument('currency')))
            elif tooltipId is None and event.hasArgument('currency'):
                currency = event.getArgument('currency')
                factory = self.__currencyTooltips.get(currency)
                if factory and factory.tooltipFactory is not None:
                    content = factory.tooltipFactory()
            if content is not None:
                window = ToolTipWindow(event, content, self.getParentWindow())
                window.load()
                window.move(event.mouse.positionX, event.mouse.positionY)
        return super(DivisionConfirmUpgradeView, self).createToolTip(event)

    def __defaultCurrenciesTooltips(self):
        model = self.viewModel
        return {Currency.GOLD: DialogTemplateTooltip(viewModel=model.goldTooltip),
         Currency.CREDITS: DialogTemplateTooltip(viewModel=model.creditsTooltip),
         Currency.CRYSTAL: DialogTemplateTooltip(viewModel=model.crystalsTooltip),
         Currency.FREE_XP: DialogTemplateTooltip(viewModel=model.freeExpTooltip)}

    def __fillCurrencyTooltipFactories(self):
        for currency, tooltip in self.__currencyTooltips.items():
            tooltip.isBackportTooltip = self.__isMoneyBalanceAvailable
            tooltip.tooltipFactory = partial(self.__moneyBalanceAvailableTooltipFactory if self.__isMoneyBalanceAvailable else self.__moneyBalanceNotAvailableTooltipFactory, currency)

    @staticmethod
    def __moneyBalanceAvailableTooltipFactory(currency):
        return createBackportTooltipContent(isSpecial=True, specialAlias=getCurrencyTooltipAlias(currency))

    @staticmethod
    def __moneyBalanceNotAvailableTooltipFactory(currency):
        params = NO_WGM_TOOLTIP_DATA.get(currency, {'header': '',
         'body': ''})
        return SimpleTooltipContent(R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent(), header=backport.text(params['header']), body=backport.text(params['body']))


class DivisionConfirmUpgradeViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, subdivisionId=None, parent=None):
        super(DivisionConfirmUpgradeViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=DivisionConfirmUpgradeView(R.views.historical_battles.lobby.DivisionConfirmUpgradeView(), subdivisionId), parent=parent)
