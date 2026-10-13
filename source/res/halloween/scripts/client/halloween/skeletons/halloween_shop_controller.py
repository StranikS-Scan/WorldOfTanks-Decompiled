# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/skeletons/halloween_shop_controller.py
from __future__ import absolute_import
from skeletons.gui.game_control import IGameController

class IHalloweenShopController(IGameController):
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

    def hasNotPurchasedBundles(self):
        raise NotImplementedError

    def checkIsEnoughBundles(self):
        raise NotImplementedError
