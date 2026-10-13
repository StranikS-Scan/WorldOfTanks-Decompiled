# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/skeletons/halloween_twitch_con_controller.py
from __future__ import absolute_import
from skeletons.gui.game_control import IGameController

class IHalloweenTwitchConController(IGameController):
    onLimitsUpdated = None
    onShopLimitsUpdated = None
    onCertificateCountUpdated = None
    onTwitchConSettingsUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def isPromoScreenEnabled(self):
        raise NotImplementedError

    def getFullCrewSound(self):
        raise NotImplementedError

    def commanders(self):
        raise NotImplementedError

    def getCommanderByID(self, commanderID):
        raise NotImplementedError

    def getCertificateTokenName(self):
        raise NotImplementedError

    def exchangeCommander(self, commandersData, callback):
        raise NotImplementedError

    def getCertificateCount(self):
        raise NotImplementedError

    def getExchangedCountByCommanderID(self, commanderID):
        raise NotImplementedError

    def getBlockCardCountByCommanderID(self, commanderID):
        raise NotImplementedError

    def canExchangeCertificateByCommanderID(self, commanderID):
        raise NotImplementedError

    def getRemainLimits(self, commanderID):
        raise NotImplementedError

    def getRemainShopLimits(self, commanderID):
        raise NotImplementedError
