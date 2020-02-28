# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/trophy_device_confirm_view.py
import logging
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.trophy_device_confirm_dialog_model import TrophyDeviceConfirmDialogModel
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.pub.dialog_window import DialogWindow, DialogContent, DialogButtons
from gui.impl.lobby.dialogs.contents.common_balance_content import CommonBalanceContent
from gui.impl.lobby.dialogs.contents.prices_content import DialogPricesContent
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
    __slots__ = ('__trophyBasicModule', '__upgradePrice', '__isGoldAutoPurhaseEnabled')
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
        super(TrophyDeviceUpgradeConfirmView, self).__init__(content=TrophyDeviceUpgradeConfirmDialogContent(trophyBasicModule), balanceContent=CommonBalanceContent(currencies=(Currency.GOLD, Currency.CREDITS)), bottomContent=DialogPricesContent(), parent=parent, enableBlur=True)
        self.__trophyBasicModule = trophyBasicModule
        self.__upgradePrice = trophyBasicModule.getUpgradePrice(self.__itemsCache.items).price
        self.__isGoldAutoPurhaseEnabled = self.__wallet.isAvailable
        return

    def _initialize(self):
        super(TrophyDeviceUpgradeConfirmView, self)._initialize()
        self.__wallet.onWalletStatusChanged += self.__onWalletStatusChanged
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyUpdated)
        self._setPreset(DialogPresets.TROPHY_DEVICE_UPGRADE)
        self.__setUpgradeCost()
        self._addButton(DialogButtons.SUBMIT, R.strings.battle_pass_2020.trophyDeviceUpgradeConfim.submit(), isFocused=True, isEnabled=self.__canPurchaseUpgrade())
        self._addButton(DialogButtons.CANCEL, R.strings.battle_pass_2020.trophyDeviceUpgradeConfim.cancel(), invalidateAll=True)

    def _finalize(self):
        self.__wallet.onWalletStatusChanged -= self.__onWalletStatusChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(TrophyDeviceUpgradeConfirmView, self)._finalize()

    def __setUpgradeCost(self):
        upgradeCost = self.gui.systemLocale.getNumberFormat(self.__upgradePrice.credits)
        with self.bottomContentViewModel.transaction() as model:
            model.valueMain.setType(Currency.CREDITS)
            model.valueMain.setValue(upgradeCost)
            model.valueMain.setNotEnough(not self.__canPurchaseUpgrade())

    def __canPurchaseUpgrade(self):
        return (self.__trophyBasicModule.mayPurchaseUpgrage(self.__itemsCache.items) or self.__trophyBasicModule.mayPurchaseUpgrageWithExchange(self.__itemsCache.items)) and self.__isGoldAutoPurhaseEnabled

    def __onMoneyUpdated(self, _):
        self.__setUpgradeCost()
        button = self._getButton(DialogButtons.SUBMIT)
        if button is not None:
            button.setIsEnabled(self.__canPurchaseUpgrade())
        return

    def __onWalletStatusChanged(self, *_):
        self.__isGoldAutoPurhaseEnabled &= self.__wallet.isAvailable
        self.__setUpgradeCost()


class TrophyDeviceUpgradeConfirmDialogContent(DialogContent):
    __slots__ = ('__trophyBasicModule', '__trophyUpgadedModule', '__strValueKPI')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, trophyBasicModule):
        super(TrophyDeviceUpgradeConfirmDialogContent, self).__init__(R.views.lobby.battle_pass.trophy_device_confirm_dialog.TrophyDeviceConfirmDialogContent(), viewModelClazz=TrophyDeviceConfirmDialogModel)
        self.__trophyBasicModule = trophyBasicModule
        self.__trophyUpgadedModule = self.__itemsCache.items.getItemByCD(trophyBasicModule.descriptor.upgradeInfo.upgradedCompDescr)
        self.__strValueKPI = self.__getValueKPI(self.__trophyBasicModule)

    def _initialize(self):
        super(TrophyDeviceUpgradeConfirmDialogContent, self)._initialize()
        with self.getViewModel().transaction() as model:
            model.setTrophyBasicName(self.__trophyBasicModule.name)
            model.setTrophyBasicImg(self.__trophyBasicModule.getShopIcon(store=RES_SHOP, size=STORE_CONSTANTS.ICON_SIZE_SMALL))
            model.setPropBaseValue(self.__strValueKPI)

    @staticmethod
    def __getValueKPI(module):
        listStrValue = []
        for kpi in module.kpi:
            percentKpi = int((kpi.value - 1) * 100)
            resValue = '{}{}%'.format('+' if percentKpi > 0 else '', percentKpi)
            listStrValue.append(resValue)

        return ''.join(listStrValue)
