# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/award_view.py
import logging
from typing import TYPE_CHECKING
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.wot_anniversary_rewards_view_model import WotAnniversaryRewardsViewModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.wot_anniversary.bonuses import getWotAnniversaryAwardPacker
from gui.wot_anniversary.sound import WOT_ANNIVERSARY_REWARD_SCREEN_SOUND
from helpers import dependency
from skeletons.gui.wot_anniversary import IWotAnniversaryController
if TYPE_CHECKING:
    from Event import Event
    from typing import Tuple, Callable, Optional, Sequence
    from gui.server_events.event_items import TokenQuest
_logger = logging.getLogger(__name__)

class WotAnniversaryAwardView(ViewImpl):
    __wotAnniversaryCtrl = dependency.descriptor(IWotAnniversaryController)
    _COMMON_SOUND_SPACE = WOT_ANNIVERSARY_REWARD_SCREEN_SOUND
    __slots__ = ('__tooltipItems',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wot_anniversary.RewardScreen(), flags=ViewFlags.VIEW, model=WotAnniversaryRewardsViewModel(), args=args, kwargs=kwargs)
        self.__tooltipItems = {}
        super(WotAnniversaryAwardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WotAnniversaryAwardView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(WotAnniversaryAwardView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def _finalize(self):
        super(WotAnniversaryAwardView, self)._finalize()
        self.__tooltipItems.clear()

    def _onLoading(self, quest, *args, **kwargs):
        super(WotAnniversaryAwardView, self)._onLoading(*args, **kwargs)
        self.__fillModel(quest)

    def _getEvents(self):
        return ((self.viewModel.onClosed, self.__onClosed), (self.__wotAnniversaryCtrl.onSettingsChanged, self.__onSettingsChange))

    def __onClosed(self):
        self.destroyWindow()

    def __fillModel(self, quest):
        filteredBonuses = [ b for b in quest.getBonuses() if b.getName() in ('vehicles', 'styleProgress') ]
        if not filteredBonuses:
            _logger.error('Can not find correct bonuses to show awardWindow')
            self.destroyWindow()
        with self.viewModel.transaction() as model:
            packBonusModelAndTooltipData(filteredBonuses, model.getMainRewards(), self.__tooltipItems, packer=getWotAnniversaryAwardPacker())

    def __onSettingsChange(self):
        if not self.__wotAnniversaryCtrl.isAvailable():
            self.destroyWindow()


class WotAnniversaryAwardWindow(LobbyNotificationWindow):
    __slots__ = ('__args',)

    def __init__(self, quest, parent=None):
        super(WotAnniversaryAwardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=WotAnniversaryAwardView(quest), parent=parent)
        self.__args = (quest.getID(),)

    def isParamsEqual(self, *args):
        return self.__args == args
