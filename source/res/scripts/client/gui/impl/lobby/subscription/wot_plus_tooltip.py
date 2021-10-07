# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/subscription/wot_plus_tooltip.py
import BigWorld
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.subscription.wot_plus_tooltip_model import WotPlusTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class WotPlusTooltip(ViewImpl):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.subscription.WotPlusTooltip())
        settings.model = WotPlusTooltipModel()
        super(WotPlusTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WotPlusTooltip, self).getViewModel()

    def _onLoading(self):
        super(WotPlusTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            isWotPlusEnabled = self.__lobbyContext.getServerSettings().isRenewableSubEnabled()
            isWotPlusSubscribed = BigWorld.player().renewableSubscription.isEnabled()
            expirationTime = BigWorld.player().renewableSubscription.getExpiryTime()
            model.setNextCharge(backport.getShortDateFormat(expirationTime))
            model.setIsActivated(isWotPlusSubscribed and isWotPlusEnabled)
