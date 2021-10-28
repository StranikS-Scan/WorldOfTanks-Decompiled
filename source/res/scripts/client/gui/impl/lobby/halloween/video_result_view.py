# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/video_result_view.py
from datetime import datetime
import WWISE
from gui.impl.gen.view_models.views.lobby.halloween.bonus_model import BonusModel
from gui.impl.lobby.halloween.tooltips.shop_vehicle_tooltip import ShopVehicleTooltip
from gui.server_events.awards_formatters import getHW21BoxRewardFormatter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.halloween.video_result_model import VideoResultModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.shared.utils.functions import replaceHyphenToUnderscore
from frameworks.wulf import Array, ViewSettings, ViewFlags
from helpers import dependency
from gui.impl import backport
from ids_generators import SequenceIDGenerator
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_event_controller import IGameEventController
from gui.impl.lobby.halloween.event_helpers import filterVehicleBonuses, getImgName
from gui.impl.lobby.halloween.sound_constants import EventHangarSound
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class VideoResultView(ViewImpl):
    eventsCache = dependency.descriptor(IEventsCache)
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, ctx, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.halloween.VideoResult())
        settings.flags = ViewFlags.VIEW
        settings.model = VideoResultModel()
        super(VideoResultView, self).__init__(settings, *args, **kwargs)
        self.__boxId = ctx.get('boxId')
        self.__callback = ctx.get('callback', None)
        self.__eventVehiclesInInventory = ctx.get('eventVehiclesInInventory', [])
        self.__isFinalReward = ctx.get('isFinalReward', False)
        self.__rewards, self.__vehicles = self.__getFormattedRewardsAndVehicles()
        self.__idGen = SequenceIDGenerator()
        self.__bonusCache = {}
        return

    @property
    def stageNum(self):
        return self.__boxId.rsplit('_', 1)[-1]

    @property
    def viewModel(self):
        return super(VideoResultView, self).getViewModel()

    def createToolTip(self, event):
        tooltipId = event.getArgument('tooltipId', None)
        if event.contentID == _R_BACKPORT_TOOLTIP:
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs), self.getParentWindow())
                window.load()
                return window
        else:
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs), self.getParentWindow())
                window.load()
                return window
        return super(VideoResultView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.halloween.tooltips.ShopVehicleTooltip():
            tankId = event.getArgument('tankId')
            return ShopVehicleTooltip(tankId)

    def _onLoading(self, *args, **kwargs):
        super(VideoResultView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self._fillModel(model)

    def _initialize(self, *args, **kwargs):
        super(VideoResultView, self)._initialize(*args, **kwargs)
        self._addListeners()

    def _finalize(self):
        self._removeListeners()
        self.__bonusCache.clear()
        if self.__callback is not None:
            self.__callback()
            self.__callback = None
        super(VideoResultView, self)._finalize()
        return

    def _addListeners(self):
        self.viewModel.onAcceptClicked += self._onGoTo
        self.viewModel.onCancelClicked += self._onCancel

    def _removeListeners(self):
        self.viewModel.onAcceptClicked -= self._onGoTo
        self.viewModel.onCancelClicked -= self._onCancel

    def _fillModel(self, model):
        if not self.gameEventController.getEventRewardController().rewardBoxesIDsInOrder:
            return
        else:
            WWISE.WW_eventGlobal(EventHangarSound.TIGER_REWARD if self.__isFinalReward else EventHangarSound.STANDARD_REWARD)
            endDate = self.eventsCache.getGameEventData()['endDate']
            endDate = datetime.utcfromtimestamp(endDate)
            model.setRewards(self.__getRewardsArray())
            model.setIsFinalReward(self.__isFinalReward)
            vehicle = None
            if self.__vehicles:
                vehicle = self.__vehicles[-1]
            model.setHasVehicle(vehicle is not None)
            if self.__isFinalReward:
                model.setTitle(R.strings.event.videoResult.title.final())
                model.setSubTitle(R.strings.event.videoResult.subTitle.final())
            else:
                model.setTitle(R.strings.event.videoResult.title())
                model.setSubTitle(R.strings.event.videoResult.subTitle())
                model.setStageNum(self.stageNum)
            if vehicle:
                level, vehType, vehName, vehId = vehicle.specialArgs[-4:]
                imgName = replaceHyphenToUnderscore(vehName.replace(':', '-'))
                if self.__isFinalReward:
                    image = R.images.gui.maps.icons.event.vehicle.c_720x330.dyn(imgName)()
                else:
                    image = R.images.gui.maps.icons.event.vehicle.c_160x133.dyn(imgName)()
                model.vehicle.setImage(image)
                model.vehicle.setType(vehType)
                model.vehicle.setId(vehId)
                model.vehicle.setLevel(level)
                model.vehicle.setName(vehicle.userName)
                model.vehicle.setTooltip(backport.text(R.strings.event.videoResult.vehicle.tooltip(), date=endDate.strftime('%d.%m.%Y'), time=endDate.strftime('%H:%M')))
            return

    def _onGoTo(self, *args):
        self.destroyWindow()

    def _onCancel(self):
        self.destroyWindow()

    def __getRewardsArray(self):
        rewards = Array()
        for _, formattedReward in enumerate(self.__rewards):
            model = BonusModel()
            model.setIcon(getImgName(formattedReward.images['big']))
            model.setLabel(formattedReward.label)
            model.setBonusType(formattedReward.bonusName)
            self.__setTooltip(model, formattedReward)
            rewards.addViewModel(model)

        return rewards

    def __setTooltip(self, model, bonus):
        tooltipId = '{}'.format(self.__idGen.next())
        self.__bonusCache[tooltipId] = bonus
        model.setTooltipId(tooltipId)

    def __getFormattedRewardsAndVehicles(self):
        if not self.gameEventController.getEventRewardController().rewardBoxesIDsInOrder:
            self.__callback = None
            return ([], None)
        else:
            rewardBox = self.gameEventController.getEventRewardController().rewardBoxesConfig[self.__boxId]
            bonuseVehicles = filterVehicleBonuses(rewardBox.bonusVehicles, self.__eventVehiclesInInventory)
            formatter = getHW21BoxRewardFormatter()
            return (formatter.format(rewardBox.bonusRewards), formatter.format(bonuseVehicles))


class VideoResultViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, ctx, parent=None):
        super(VideoResultViewWindow, self).__init__(content=VideoResultView(ctx), parent=parent)
