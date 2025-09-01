# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/vehicle_hub_wallet_presenter.py
from __future__ import absolute_import
from gui.impl.lobby.page.wallet_presenter import WalletPresenter, GoldProvider, CreditsProvider, CrystalProvider, FreeXpProvider

class VehicleHubWalletPresenter(WalletPresenter):

    def __init__(self):
        super(VehicleHubWalletPresenter, self).__init__((CrystalProvider(),
         GoldProvider(),
         CreditsProvider(),
         FreeXpProvider()))
