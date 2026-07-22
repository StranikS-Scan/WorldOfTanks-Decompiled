# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/lobby/tank_academy/tank_academy_rewards_view.py
import logging
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.server_events.pm3_constants import SOUNDS
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import VehiclesBonus
from gui.shared.event_dispatcher import selectVehicleInHangar
from helpers import dependency
from shared_utils import first, findFirst
from skeletons.gui.game_control import ITankAcademyController
from tank_academy.gui.shared.bonus_packers import packRewardsModelAndTooltipData
from tank_academy.gui.shared.event_dispatcher import showTankAcademy, showTankAcademyVehicleSelection
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.tank_academy_rewards_view_model import TankAcademyRewardsViewModel, State
_logger = logging.getLogger(__name__)

class TankAcademyRewardsView(ViewImpl):
    __slots__ = ('__tooltipData', '__questOrder', '__isRewardScreenChain', '__isFirstRewardScreenChain', '__rewards')
    __tankAcademyController = dependency.descriptor(ITankAcademyController)

    def __init__(self, ctx):
        settings = ViewSettings(layoutID=R.views.tank_academy.lobby.tank_academy.TankAcademyRewardsView(), model=TankAcademyRewardsViewModel())
        self.__tooltipData = {}
        self.__questOrder = ctx.keys()[0]
        questData = ctx[self.__questOrder]
        self.__isRewardScreenChain = questData.get('isRewardScreenChain', False)
        self.__isFirstRewardScreenChain = questData.get('isFirstRewardScreenChain', False)
        self.__rewards = questData.get('detailedRewards', {})
        super(TankAcademyRewardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankAcademyRewardsView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData else None
            if window is not None:
                window.load()
            return window
        else:
            return super(TankAcademyRewardsView, self).createToolTip(event)

    def onClose(self):
        self.soundManager.setState(SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_GROUP, SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_OFF)
        self.destroyWindow()

    def onRewardsSelection(self):
        tokensRewards = self.__rewards.get('tokens', {})
        if tokensRewards is None:
            _logger.error('No tokens reward to open selection')
            return
        else:
            offerToken = findFirst(self.__tankAcademyController.isTAOfferToken, tokensRewards.keys())
            if offerToken is None:
                _logger.error('No delayed reward token to open selection')
                return
            showTankAcademyVehicleSelection(offerToken)
            self.destroyWindow()
            return

    def onNextTask(self):
        showTankAcademy()
        self.destroyWindow()

    def onHangarPreview(self):
        vehicle = first(self.__rewards.get(VehiclesBonus.VEHICLES_BONUS, []))
        if vehicle is None:
            _logger.error('No vehicle in rewards to open hangar preview')
            return
        else:
            vehicleCD = first(vehicle.keys())
            if vehicleCD is None:
                _logger.error('No vehicle cd in vehicles rewards to open hangar preview')
                return
            selectVehicleInHangar(vehicleCD)
            self.destroyWindow()
            return

    def _onLoading(self, *args, **kwargs):
        super(TankAcademyRewardsView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setStage(self.__questOrder)
            model.setState(self.__getState())
            mainRewards = model.getMainRewards()
            mainRewards.clear()
            otherRewards = model.getRewards()
            otherRewards.clear()
            packRewardsModelAndTooltipData(self.__rewards, mainRewards, otherRewards, self.__tooltipData)
            self.soundManager.setState(SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_GROUP, SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_ON)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.onClose),
         (self.viewModel.goToRewardsSelection, self.onRewardsSelection),
         (self.viewModel.goToNextTask, self.onNextTask),
         (self.viewModel.goToHangarPreview, self.onHangarPreview))

    def __getState(self):
        if self.__isRewardScreenChain:
            if self.__isFirstRewardScreenChain:
                return State.REWARDSCREENCHAIN
            return State.ENDREWARDSCREENCHAIN
        firstQuest = self.__tankAcademyController.getFirstQuest()
        if firstQuest and firstQuest.getOrder() == self.__questOrder:
            return State.FIRST
        finalQuest = self.__tankAcademyController.getFinalQuest()
        return State.FINAL if finalQuest and finalQuest.getOrder() == self.__questOrder else State.REGULAR

    def __getBackportTooltipData(self, event):
        index = event.getArgument('tooltipId')
        if index is None:
            _logger.error('No tooltipId for backport tooltip')
            return
        else:
            return self.__tooltipData.get(index)


class TankAcademyRewardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None, ctx=None):
        super(TankAcademyRewardsViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=TankAcademyRewardsView(ctx=ctx), parent=parent)
