# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/skeletons/ls_shop_controller.py
from skeletons.gui.game_control import IGameController

class ILSShopController(IGameController):
    onShopSettingsUpdated = None
    onBundlesUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def keyBundles(self):
        raise NotImplementedError

    def getBundleByID(self, bundleID):
        raise NotImplementedError

    def getKeysInBundle(self, bundleID):
        raise NotImplementedError

    def purchaseBundle(self, bundleID, int):
        raise NotImplementedError

    def getPurchaseCount(self, bundleID):
        raise NotImplementedError

    def checkIsEnoughBundles(self):
        raise NotImplementedError
