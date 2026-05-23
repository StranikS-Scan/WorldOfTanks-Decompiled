# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/skeletons/open_bundle_controller.py
from __future__ import absolute_import
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from typing import Dict, List
    from gui.server_events.bonuses import SimpleBonus
    from open_bundle.helpers.server_settings import BundlesConfig, BundleConfig

class IOpenBundleController(IGameController):
    onSettingsChanged = None
    onStatusChanged = None

    @property
    def config(self):
        raise NotImplementedError

    @property
    def bundleIDs(self):
        raise NotImplementedError

    def isEnabled(self, bundleID):
        raise NotImplementedError

    def getBundle(self, bundleID):
        raise NotImplementedError

    def isBundleActive(self, bundleID):
        raise NotImplementedError

    def isAllBundleCellsReceived(self, bundleID):
        raise NotImplementedError

    def getBundleTimeLeft(self, bundleID):
        raise NotImplementedError

    def isRareCell(self, bundleID, cellName):
        raise NotImplementedError

    def isUnicNotificationCell(self, bundleID, cellName):
        raise NotImplementedError

    def getCellBonusInfo(self, bundleID, cellName):
        raise NotImplementedError

    def getReceivedCells(self, bundleID):
        raise NotImplementedError

    def getBonusPriority(self, bonus):
        raise NotImplementedError

    def isBonusVisible(self, bonus):
        raise NotImplementedError

    def isRandomPrb(self):
        raise NotImplementedError

    def selectRandomBattle(self, callback):
        raise NotImplementedError
