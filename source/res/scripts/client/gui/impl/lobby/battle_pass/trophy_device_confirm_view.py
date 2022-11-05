# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/trophy_device_confirm_view.py
import logging
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.trophy_device_confirm_bonus_model import TrophyDeviceConfirmBonusModel
from gui.impl.gen.view_models.views.lobby.battle_pass.trophy_device_confirm_dialog_model import TrophyDeviceConfirmDialogModel
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.pub.dialog_window import DialogWindow, DialogContent, DialogButtons
from gui.impl.lobby.dialogs.contents.common_balance_content import CommonBalanceContent
from gui.impl.lobby.dialogs.contents.prices_content import DialogPricesContent
from gui.shared.gui_items import getKpiValueString
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IWalletController
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.framework.entities.View import ViewKey
_logger = logging.getLogger(__name__)

class TrophyDeviceUpgradeConfirmView(DialogWindow):
    __slots__ = ('__trophyBasicModule', '__upgradePrice', '__goldOperationsEnabled')
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, trophyBasicModule, parent):
        if parent is None:
            app = self.__appLoader.getApp()
            view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY))
            if view is not None:
                parent = view.getParentWindow()
            else:
                parent = None
        super(TrophyDeviceUpgradeConfirmView, self).__init__(content=TrophyDeviceUpgradeConfirmDialogContent(trophyBasicModule), balanceContent=CommonBalanceContent(currencies=(Currency.GOLD, Currency.CREDITS)), bottomContent=DialogPricesContent(), parent=parent)
        self.__trophyBasicModule = trophyBasicModule
        self.__upgradePrice = trophyBasicModule.getUpgradePrice(self.__itemsCache.items).price
        self.__goldOperationsEnabled = self.__wallet.isAvailable
        return

    def _initialize(self):
        super(TrophyDeviceUpgradeConfirmView, self)._initialize()
        self.__wallet.onWalletStatusChanged += self.__onWalletStatusChanged
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)
        self._setPreset(DialogPresets.TROPHY_DEVICE_UPGRADE)
        self.__setUpgradeCost()
        canUpgrade = self.__canPurchaseUpgrade()
        self._addButton(DialogButtons.SUBMIT, R.strings.battle_pass.trophyDeviceUpgradeConfim.submit(), isFocused=True, isEnabled=canUpgrade, tooltipBody=self.__getSubmitBtnTooltip(canUpgrade))
        self._addButton(DialogButtons.CANCEL, R.strings.battle_pass.trophyDeviceUpgradeConfim.cancel(), invalidateAll=True)

    def _finalize(self):
        self.__wallet.onWalletStatusChanged -= self.__onWalletStatusChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(TrophyDeviceUpgradeConfirmView, self)._finalize()

    def _getResultData(self):
        return {'needMoreCurrency': not self.__trophyBasicModule.mayPurchaseUpgrade(self.__itemsCache.items) and self.__trophyBasicModule.mayPurchaseUpgradeWithExchange(self.__itemsCache.items)}

    def __setUpgradeCost(self):
        upgradeCost = self.gui.systemLocale.getNumberFormat(self.__upgradePrice.credits)
        with self.bottomContentViewModel.transaction() as model:
            model.valueMain.setType(Currency.CREDITS)
            model.valueMain.setValue(upgradeCost)
            model.valueMain.setNotEnough(not self.__trophyBasicModule.mayPurchaseUpgrade(self.__itemsCache.items))

    def __canPurchaseUpgrade(self):
        return (self.__trophyBasicModule.mayPurchaseUpgrade(self.__itemsCache.items) or self.__trophyBasicModule.mayPurchaseUpgradeWithExchange(self.__itemsCache.items)) and self.__goldOperationsEnabled

    def __onMoneyUpdated(self, _):
        self.__setUpgradeCost()
        button = self._getButton(DialogButtons.SUBMIT)
        if button is not None:
            canUpgrade = self.__canPurchaseUpgrade()
            button.setIsEnabled(canUpgrade)
            button.setTooltipBody(self.__getSubmitBtnTooltip(canUpgrade))
        return

    def __onWalletStatusChanged(self, *_):
        self.__goldOperationsEnabled &= self.__wallet.isAvailable
        self.__setUpgradeCost()

    def __getSubmitBtnTooltip(self, canUpgrade):
        return R.invalid() if canUpgrade else R.strings.battle_pass.trophyDeviceUpgradeConfim.submitTooltip()


class TrophyDeviceUpgradeConfirmDialogContent(DialogContent):
    __slots__ = ('__trophyBasicModule', '__trophyUpgadedModule', '__strValueKPI')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, trophyBasicModule):
        super(TrophyDeviceUpgradeConfirmDialogContent, self).__init__(R.views.lobby.battle_pass.trophy_device_confirm_dialog.TrophyDeviceConfirmDialogContent(), viewModelClazz=TrophyDeviceConfirmDialogModel)
        self.__trophyBasicModule = trophyBasicModule
        self.__trophyUpgadedModule = self.__itemsCache.items.getItemByCD(trophyBasicModule.descriptor.upgradeInfo.upgradedCompDescr)

    def _initialize(self):
        super(TrophyDeviceUpgradeConfirmDialogContent, self)._initialize()
        with self.getViewModel().transaction() as model:
            model.setTrophyBasicName(self.__trophyBasicModule.name)
            model.setTrophyBasicImg(self.__trophyBasicModule.getShopIcon(store=RES_SHOP, size=STORE_CONSTANTS.ICON_SIZE_SMALL))
            for baseKpi, upgradedKpi in zip(self.__trophyBasicModule.getKpi(), self.__trophyUpgadedModule.getKpi()):
                if baseKpi.name != upgradedKpi.name:
                    _logger.error('KPI in basic and upgraded module doesnt has same order')
                    continue
                if baseKpi.value == upgradedKpi.value:
                    continue
                bonus = TrophyDeviceConfirmBonusModel()
                bonus.setKpiName(baseKpi.name)
                bonus.setBaseValue(getKpiValueString(baseKpi, baseKpi.value))
                bonus.setUpgradedValue(getKpiValueString(upgradedKpi, upgradedKpi.value))
                model.getBonuses().addViewModel(bonus)
