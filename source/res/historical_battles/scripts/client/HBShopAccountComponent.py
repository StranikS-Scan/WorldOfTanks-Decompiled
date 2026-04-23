# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBShopAccountComponent.py
from adisp import adisp_async
from EventShopAccountComponentBase import EventShopAccountComponentBase, EventShopBundlePurchaseProcessor
from historical_battles.settings import HBShop
from historical_battles_common import account_commands
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from historical_battles_common.hb_constants import HB_SHOP_GAME_PARAMS_KEY
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils import decorators

class HBShopAccountComponent(EventShopAccountComponentBase):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__shop = HBShop()
        super(HBShopAccountComponent, self).__init__()

    def showErrorSystemMessage(self):
        SystemMessages.pushMessage(backport.text(R.strings.hb_shop.errors.serverError()), SystemMessages.SM_TYPE.Error)

    def showCooldownErrorSystemMessage(self):
        SystemMessages.pushMessage(backport.text(R.strings.hb_shop.errors.serverCooldownError()), SystemMessages.SM_TYPE.MediumInfo)

    @adisp_async
    @decorators.adisp_process('buyItem')
    def processPurchaseBundle(self, bundleID, count, callback):
        result = yield EventShopBundlePurchaseProcessor(self._shopBundles[bundleID], count, self).request()
        if result.success:
            callback(result)
        elif result.errStr == 'COOLDOWN':
            self.showCooldownErrorSystemMessage()
        else:
            self.showErrorSystemMessage()

    @property
    def _purchaseCmdID(self):
        return account_commands.CMD_PURCHASE_HB_SHOP_BUNDLE

    def _updateShopData(self, serverSettingsDiff):
        data = serverSettingsDiff[HB_SHOP_GAME_PARAMS_KEY]
        self.__shop = self.__shop.replace(data)

    def _isShopDataUpdated(self, serverSettingsDiff):
        return False if HB_SHOP_GAME_PARAMS_KEY not in serverSettingsDiff else True

    @property
    def _shopData(self):
        return self.__shop.asDict()
