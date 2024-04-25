# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBShopAccountComponent.py
from adisp import adisp_async
from EventShopAccountComponentBase import EventShopAccountComponentBase, EventShopBundlePurchaseProcessor
from historical_battles_common import account_commands
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from historical_battles_common.hb_constants import HB_SHOP_GAME_PARAMS_KEY
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils import decorators
from gui.shared.gui_items.processors import plugins as proc_plugs

class HBShopAccountComponent(EventShopAccountComponentBase):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def showErrorSystemMessage(self):
        SystemMessages.pushMessage(backport.text(R.strings.hb_shop.errors.serverError()), SystemMessages.SM_TYPE.Error)

    @adisp_async
    @decorators.adisp_process('buyItem')
    def processPurchaseBundle(self, bundleID, count, callback):
        result = yield EventShopBundlePurchaseProcessor(self._shopBundles[bundleID], count, self).request()
        if not result.success:
            self.showErrorSystemMessage()
        callback(result)

    @adisp_async
    @decorators.adisp_process('buyItem')
    def processPurchaseMainPrizeBundle(self, bundleID, crewType, withAmmo, callback):
        result = yield HBShopMainPrizeBundlePurchaseProcessor(self._shopBundles[bundleID], self, crewType, withAmmo).request()
        if not result.success:
            self.showErrorSystemMessage()
        callback(result)

    def purchaseMainPrize(self, bundleID, crewType, withAmmo, callback=None):
        self.entity._doCmdIntArrStrArr(account_commands.CMD_PURCHASE_HB_SHOP_MAIN_PRIZE, [int(crewType), int(withAmmo)], [bundleID], callback)

    @property
    def _purchaseCmdID(self):
        return account_commands.CMD_PURCHASE_HB_SHOP_BUNDLE

    @property
    def _shopData(self):
        return self.lobbyContext.getServerSettings().hbShop.asDict()

    def _isShopDataUpdated(self, diff):
        if ('serverSettings', '_r') in diff:
            return HB_SHOP_GAME_PARAMS_KEY in diff[('serverSettings', '_r')]
        return HB_SHOP_GAME_PARAMS_KEY in diff['serverSettings'] if 'serverSettings' in diff else False


class HBShopMainPrizeBundlePurchaseProcessor(EventShopBundlePurchaseProcessor):

    def __init__(self, bundle, shopComponent, crewType, withAmmo):
        self._crewType = crewType
        self._withAmmo = withAmmo
        self._shopComponent = shopComponent
        super(HBShopMainPrizeBundlePurchaseProcessor, self).__init__(bundle, 1, shopComponent)

    def _getPlugins(self):
        plugins = super(HBShopMainPrizeBundlePurchaseProcessor, self)._getPlugins()
        plugins.append(proc_plugs.VehicleSlotsConfirmator(not self._withAmmo))
        return plugins

    def _request(self, callback):
        self._shopComponent.purchaseMainPrize(self._bundle.id, self._crewType, self._withAmmo, lambda requestID, code, errorCode, *args, **kwargs: self._response(code, callback, errorCode))
