# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/order_info_view.py
from PlayerEvents import g_playerEvents
from adisp import adisp_process
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.server_events.events_dispatcher import showMissionsCategories
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.info_views.info_bonuses_view_model import InfoBonusesViewModel
from historical_battles.gui.impl.lobby.base_event_view import BaseEventView
from historical_battles.gui.prb_control.prb_config import PREBATTLE_ACTION_NAME
from historical_battles.gui.sounds.sound_constants import BOOSTERS_SHOP_SOUND_SPACE
from historical_battles_common.hb_constants import HB_BATTLE_QUESTS_PREFIX
from shared_utils import first
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.server_events import IEventsCache
from gui.impl.pub.lobby_window import LobbyWindow
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
import logging
_logger = logging.getLogger(__name__)

class OrderInfoView(BaseEventView):
    _COMMON_SOUND_SPACE = BOOSTERS_SHOP_SOUND_SPACE
    _eventsCache = dependency.descriptor(IEventsCache)
    _platoonCtrl = dependency.descriptor(IPlatoonController)

    def __init__(self, layoutID):
        viewModel = InfoBonusesViewModel()
        settings = ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, viewModel)
        super(OrderInfoView, self).__init__(settings)
        g_playerEvents.onEnqueued += self._closeHandler
        self._platoonCtrl.onMembersUpdate += self._checkPlatoonStatus
        viewModel.onClose += self._closeHandler
        viewModel.onQuestButtonClick += self._questButtonClickHandler

    def _finalize(self):
        viewModel = self.getViewModel()
        g_playerEvents.onEnqueued -= self._closeHandler
        self._platoonCtrl.onMembersUpdate -= self._checkPlatoonStatus
        viewModel.onClose -= self._closeHandler
        viewModel.onQuestButtonClick -= self._questButtonClickHandler
        super(OrderInfoView, self)._finalize()

    def onPrbEntitySwitched(self):
        super(OrderInfoView, self).onPrbEntitySwitched()
        self.destroyWindow()

    def _closeHandler(self, *_):
        self.destroyWindow()

    def _checkPlatoonStatus(self):
        if self._platoonCtrl.isInQueue():
            self.destroyWindow()

    @adisp_process
    def _questButtonClickHandler(self):
        groups = self._eventsCache.getGroups()
        group = first((group for group in groups.itervalues() if group.getID().startswith(HB_BATTLE_QUESTS_PREFIX)))
        yield g_prbLoader.getDispatcher().doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        if group:
            showMissionsCategories(groupID=group.getID())
        else:
            _logger.warning('There is no group with id = ' + HB_BATTLE_QUESTS_PREFIX + ". Can't show missions")


class HBOrderInfoView(LobbyWindow):

    def __init__(self, layoutID):
        super(HBOrderInfoView, self).__init__(wndFlags=WindowFlags.WINDOW, content=OrderInfoView(layoutID=layoutID))
