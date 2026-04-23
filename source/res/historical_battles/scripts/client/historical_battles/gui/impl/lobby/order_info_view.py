# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/order_info_view.py
from PlayerEvents import g_playerEvents
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.order_info_view_model import OrderInfoViewModel
from historical_battles.gui.impl.lobby.base_event_view import BaseEventView
from historical_battles.gui.sounds.sound_constants import BOOSTERS_SHOP_SOUND_SPACE
from historical_battles.gui.impl.lobby.tooltips.hb_coin_tooltip import HbCoinTooltip
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.server_events import IEventsCache
from gui.impl.pub.lobby_window import LobbyWindow
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
import logging
_logger = logging.getLogger(__name__)

class OrderInfoView(BaseEventView):
    _COMMON_SOUND_SPACE = BOOSTERS_SHOP_SOUND_SPACE
    _eventsCache = dependency.descriptor(IEventsCache)
    _platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, OrderInfoViewModel())
        super(OrderInfoView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(OrderInfoView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return HbCoinTooltip() if contentID == R.views.historical_battles.lobby.tooltips.HbCoinTooltip() else None

    def _onLoading(self, *args, **kwargs):
        super(OrderInfoView, self)._onLoading(args, kwargs)
        g_playerEvents.onEnqueued += self._closeHandler
        self._platoonCtrl.onMembersUpdate += self._checkPlatoonStatus
        with self.viewModel.transaction() as model:
            front = self._gameEventController.frontController.getSelectedFront()
            model.setFrontName(front.getName())

    def _finalize(self):
        g_playerEvents.onEnqueued -= self._closeHandler
        self._platoonCtrl.onMembersUpdate -= self._checkPlatoonStatus
        super(OrderInfoView, self)._finalize()

    def onPrbEntitySwitched(self):
        super(OrderInfoView, self).onPrbEntitySwitched()
        self.destroyWindow()

    def _closeHandler(self, *_):
        self.destroyWindow()

    def _checkPlatoonStatus(self):
        if self._platoonCtrl.isInQueue():
            self.destroyWindow()


class HBOrderInfoView(LobbyWindow):

    def __init__(self, layoutID):
        super(HBOrderInfoView, self).__init__(wndFlags=WindowFlags.WINDOW, content=OrderInfoView(layoutID=layoutID))
