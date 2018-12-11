# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_level_up_view.py
from collections import namedtuple
import GUI
from frameworks.wulf import ViewFlags, WindowFlags
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.gen.view_models.new_year.views.new_year_level_up_view_model import NewYearLevelUpViewModel
from gui.impl.wrappers.background_blur import WGUIBackgroundBlurSupportImpl
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.server_events.awards_formatters import getPackRentNewYearAwardPacker, NewYearQuestBonusComposer
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.impl.backport_tooltip import BackportTooltipWindow, TooltipData
from gui.impl.auxiliary.rewards_helper import getRewardRendererModelPresenter, LootVideoWithCongratsRewardPresenter
from gui.impl.auxiliary.rewards_helper import VehicleCompensationModelPresenter, LootVehicleRewardPresenter
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
_VEHICLES_BONUS_NAME = 'vehicles'
_COMPENSATION_PRESENTERS = {_VEHICLES_BONUS_NAME: VehicleCompensationModelPresenter()}
_MODEL_PRESENTERS = {_VEHICLES_BONUS_NAME: LootVehicleRewardPresenter(),
 'tmanToken': LootVideoWithCongratsRewardPresenter(LootCongratsTypes.CONGRAT_TYPE_TANKMAN)}
_RewardsData = namedtuple('_RewardsData', ('level', 'data'))

class NewYearLevelUpWindowContent(ViewImpl):
    __slots__ = ('__rewards', '__blur', '__tooltipData')

    def __init__(self, *args, **kwargs):
        super(NewYearLevelUpWindowContent, self).__init__(R.views.newYearLevelUpView, ViewFlags.VIEW, NewYearLevelUpViewModel, *args, **kwargs)
        self.__tooltipData = {}
        self.__rewards = None
        self.__blur = WGUIBackgroundBlurSupportImpl(blur3dScene=not GUI.WGUIBackgroundBlur().enable)
        return

    def createToolTip(self, event):
        if event.contentID == R.views.backportTooltipContent:
            tooltipId = event.getArgument('tooltipId')
            window = None
            if tooltipId is not None:
                window = BackportTooltipWindow(self.__tooltipData[tooltipId], self.getParentWindow())
                window.load()
            return window
        else:
            return super(NewYearLevelUpWindowContent, self).createToolTip(event)

    def _initialize(self, ctx):
        super(NewYearLevelUpWindowContent, self)._initialize()
        NewYearSoundsManager.playEvent(NewYearSoundEvents.LEVEL_UP)
        self.__rewards = [ _RewardsData(lvl, self.__getRewards(data)) for lvl, data in ctx.iteritems() ]
        if self.__rewards:
            self.__setRewards(*self.__rewards.pop(0))
        self.getViewModel().onClose += self.__onClose
        self.getViewModel().onCollectRewards += self.__onCollectRewards
        self.__blur.enable(APP_CONTAINERS_NAMES.OVERLAY, [APP_CONTAINERS_NAMES.VIEWS,
         APP_CONTAINERS_NAMES.WINDOWS,
         APP_CONTAINERS_NAMES.SUBVIEW,
         APP_CONTAINERS_NAMES.BROWSER,
         APP_CONTAINERS_NAMES.DIALOGS])
        g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_LEVEL_UP_WINDOW_CONTENT_LOADED), scope=EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        super(NewYearLevelUpWindowContent, self)._finalize()
        g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_LEVEL_UP_WINDOW_CONTENT_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)
        self.getViewModel().onClose -= self.__onClose
        self.getViewModel().onCollectRewards -= self.__onCollectRewards
        self.__blur.disable()

    def __onCloseAction(self):
        if self.__rewards:
            NewYearSoundsManager.playEvent(NewYearSoundEvents.LEVEL_UP)
            self.__setRewards(*self.__rewards.pop(0))
        else:
            self.destroyWindow()

    def __onClose(self):
        self.__onCloseAction()

    def __onCollectRewards(self):
        self.__onCloseAction()

    def __setRewards(self, level, rewards):
        with self.getViewModel().transaction() as model:
            model.setLevel(level)
            rewardsList = model.getRewards()
            rewardsList.clear()
            for index, reward in enumerate(rewards):
                if reward.get('bonusName') == _VEHICLES_BONUS_NAME:
                    model.setContainsVehicle(True)
                formatter = getRewardRendererModelPresenter(reward, _MODEL_PRESENTERS, _COMPENSATION_PRESENTERS)
                rewardRender = formatter.getModel(reward, index)
                rewardsList.addViewModel(rewardRender)
                self.__tooltipData[index] = TooltipData(tooltip=reward.get('tooltip', None), isSpecial=reward.get('isSpecial', False), specialAlias=reward.get('specialAlias', ''), specialArgs=reward.get('specialArgs', None))

            rewardsList.invalidate()
        return

    @classmethod
    def __getRewards(cls, bonuses):
        formatter = NewYearQuestBonusComposer(getPackRentNewYearAwardPacker())
        formattedBonuses = formatter.getFormattedBonuses(bonuses, size='big')
        return formattedBonuses


class NewYearLevelUpWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(NewYearLevelUpWindow, self).__init__(wndFlags=WindowFlags.OVERLAY, decorator=None, content=NewYearLevelUpWindowContent(*args, **kwargs), parent=None)
        return
