# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/wot_anniversary_award_view.py
import WWISE
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.wot_anniversary_award_view_model import WotAnniversaryAwardViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import getNonQuestBonuses
from gui.wot_anniversary.wot_anniversary_bonuses_packers import packBonusModelAndTooltipData
from gui.wot_anniversary.wot_anniversary_helpers import getQuestNeededTokensCount
from helpers import dependency
from skeletons.gui.game_control import IWotAnniversaryController
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class WotAnniversaryAwardView(ViewImpl):
    __wotAnniversaryCtrl = dependency.descriptor(IWotAnniversaryController)
    __slots__ = ('__tooltipItems',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wot_anniversary.AwardScreen())
        settings.flags = ViewFlags.VIEW
        settings.model = WotAnniversaryAwardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__tooltipItems = {}
        super(WotAnniversaryAwardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WotAnniversaryAwardView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClose += self.__onClose

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        self.__tooltipItems.clear()

    def _onLoading(self, questID, rawAwards, *args, **kwargs):
        super(WotAnniversaryAwardView, self)._onLoading(*args, **kwargs)
        WWISE.WW_eventGlobal(backport.sound(R.sounds.ev_bday_12_reward()))
        self.__fillModel(questID, rawAwards)

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(WotAnniversaryAwardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = self.__getBackportTooltipData(event)
        return getRewardTooltipContent(event, tooltipData)

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def __onClose(self):
        self.destroyWindow()

    def __fillModel(self, questID, rawAwards):
        bonuses = []
        for key, value in rawAwards.iteritems():
            bonuses.extend(getNonQuestBonuses(key, value, ctx=None))

        with self.viewModel.transaction() as tx:
            mainBonusesModel = tx.mainRewards
            packBonusModelAndTooltipData(bonuses, mainBonusesModel, self.__tooltipItems)
            tx.setQuestsCount(getQuestNeededTokensCount(self.__wotAnniversaryCtrl.getQuests().get(questID)))
        return


class WotAnniversaryAwardWindow(LobbyNotificationWindow):
    __slots__ = ('__args',)

    def __init__(self, questID, rawAwards, parent=None):
        super(WotAnniversaryAwardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=WotAnniversaryAwardView(questID, rawAwards), parent=parent)
        self.__args = (questID, rawAwards)

    def isParamsEqual(self, *args):
        return self.__args == args
