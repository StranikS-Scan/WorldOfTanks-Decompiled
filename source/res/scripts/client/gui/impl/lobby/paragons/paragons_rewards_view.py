# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/paragons_rewards_view.py
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import makeRewardModels
from gui.impl.lobby.paragons.paragons_window_events import showParagonsSelectRewardsWindow
from gui.impl.lobby.paragons.tooltips.vehicle_select_tooltip import VehicleSelectTooltip
from gui.impl.lobby.paragons.tooltips.branch_select_tooltip import BranchSelectTooltip
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.paragons.paragons_rewards_view_model import ParagonsRewardsViewModel
from gui.impl.pub import ViewImpl
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
import logging
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.event_dispatcher import showHangar
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

class ParagonsRewardsView(ViewImpl):
    __slots__ = ('__tooltipData', '__chapterLevel', '__rewards', '__isVehicleSelected', '__chapterID')

    def __init__(self, layoutID, rewards, chapter=None, level=None, isVehicleSelected=False):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = ParagonsRewardsViewModel()
        self.__chapterLevel = level
        self.__rewards = rewards
        self.__tooltipData = {}
        self.__isVehicleSelected = isVehicleSelected
        self.__chapterID = chapter
        super(ParagonsRewardsView, self).__init__(settings)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ParagonsRewardsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.paragons.tooltips.VehicleSelectTooltip():
            return VehicleSelectTooltip(layoutID=R.views.lobby.paragons.tooltips.VehicleSelectTooltip())
        if contentID == R.views.lobby.paragons.tooltips.BranchSelectTooltip():
            tooltipData = self.getTooltipData(event)
            return BranchSelectTooltip(layoutID=R.views.lobby.paragons.tooltips.BranchSelectTooltip(), paragonsUnlockID=tooltipData.specialArgs[0])
        return super(ParagonsRewardsView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    @property
    def viewModel(self):
        return super(ParagonsRewardsView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onShowVehicleInHangar, self.__onShowVehicleInHangar), (self.viewModel.onSelectVehicleAsReward, self.__onSelectVehicleAsReward))

    def _onLoading(self, *args, **kwargs):
        super(ParagonsRewardsView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as viewModel:
            if self.__chapterLevel is not None:
                viewModel.setDescription(backport.text(R.strings.paragons.rewards.notification(), level=self.__chapterLevel))
                viewModel.setChapterLevel(self.__chapterLevel)
            viewModel.setSelectedVehicle(self.__isVehicleSelected)
            if not self.__isVehicleSelected:
                makeRewardModels(self.__rewards, viewModel.getMainRewards(), viewModel.getRewards(), tooltipData=self.__tooltipData, levelID=self.__chapterLevel if self.__chapterLevel is not None else 1)
            else:
                makeRewardModels({k:v for k, v in self.__rewards.iteritems() if k == 'vehicles'}, viewModel.getMainRewards(), viewModel.getRewards(), tooltipData=self.__tooltipData)
        return

    def __onClose(self):
        self.destroyWindow()

    def __onShowVehicleInHangar(self):
        for key, value in self.__rewards.iteritems():
            if key != 'vehicles':
                continue
            bonuses = getNonQuestBonuses(key, value)
            if len(bonuses) != 1:
                raise SoftException('Bonuses size is not 1, might be a problem in this place')
            if len(bonuses[0].getVehicles()) != 1:
                raise SoftException('Vehicles size is not 1, might be a problem in this place')
            vehicle, _ = bonuses[0].getVehicles()[0]
            if not vehicle.isInInventory:
                _logger.warning('vehicle is not in inventory, showing is impossible')
                continue
            showHangar()
            g_currentVehicle.selectVehicle(vehicle.invID)
            self.destroyWindow()
            return

    @args2params(str)
    def __onSelectVehicleAsReward(self, entCode):
        showParagonsSelectRewardsWindow(chapterID=self.__chapterID, levelID=self.__chapterLevel, entitlementID=entCode)
        self.destroyWindow()


class ParagonsRewardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rewards, chapter=None, level=None, isVehicleSelected=False, parent=None):
        super(ParagonsRewardsViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ParagonsRewardsView(R.views.lobby.paragons.ParagonsRewardsView(), rewards, chapter=chapter, level=level, isVehicleSelected=isVehicleSelected), layer=WindowLayer.FULLSCREEN_WINDOW, parent=parent)
