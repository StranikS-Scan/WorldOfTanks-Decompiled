# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_style_reward_view.py
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import SortedBonusNameQuestsBonusComposer
from gui.impl.auxiliary.rewards_helper import getRewardRendererModelPresenter
from gui.impl.backport.backport_tooltip import createTooltipDataByDict, showBackportTooltip
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_style_reward_view_model import NewYearStyleRewardViewModel
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.new_year.new_year_helper import nyBonusSortOrder
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from frameworks.wulf import ViewSettings, WindowLayer
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.server_events.awards_formatters import getNYAwardsPacker, AWARDS_SIZES
from helpers import dependency
from items.components.ny_constants import YEARS_INFO, ToySettings
from items.new_year import getCollectionByIntID
from skeletons.new_year import INewYearController
_MAX_CAPACITY = 8

class NewYearStyleRewardView(ViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    __slots__ = ('__tooltipData', '__rewards')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_style_reward_view.NewYearStyleRewardView())
        settings.model = NewYearStyleRewardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearStyleRewardView, self).__init__(settings)
        self.__tooltipData = {}
        self.__rewards = None
        return

    @property
    def viewModel(self):
        return super(NewYearStyleRewardView, self).getViewModel()

    def createToolTip(self, event):
        backportWindow = showBackportTooltip(event, self.__tooltipData, self.getParentWindow())
        return backportWindow or super(NewYearStyleRewardView, self).createToolTip(event)

    def _initialize(self, rewards):
        super(NewYearStyleRewardView, self)._initialize()
        self.__rewards = rewards
        NewYearSoundsManager.playEvent(NewYearSoundEvents.AWARD_STYLE_SCREEN)
        self.viewModel.onClose += self.__onClose
        if self.__rewards:
            self.__setRewards(*self.__rewards.popitem())
        setOverlayHangarGeneral(True)

    def _finalize(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.AWARD_STYLE_SCREEN_EXIT)
        setOverlayHangarGeneral(False)
        super(NewYearStyleRewardView, self)._finalize()
        self.__rewards = None
        self.viewModel.onClose -= self.__onClose
        return

    def __setRewards(self, collectionStrID, rewards):
        rewards = self.__getRewards(rewards)
        collectionIntID = YEARS_INFO.getCollectionIntID(collectionStrID)
        with self.getViewModel().transaction() as model:
            year, collectionName = getCollectionByIntID(collectionIntID)
            model.setStyleStr('{}_{}'.format(collectionName, year))
            model.setIsMega(collectionName == ToySettings.MEGA_TOYS)
            rewardsList = model.getRewards()
            rewardsList.clear()
            for index, reward in enumerate(rewards):
                formatter = getRewardRendererModelPresenter(reward)
                rewardRender = formatter.getModel(reward, index)
                rewardsList.addViewModel(rewardRender)
                self.__tooltipData[index] = createTooltipDataByDict(reward)

            rewardsList.invalidate()

    @classmethod
    def __getRewards(cls, bonuses):
        formatter = SortedBonusNameQuestsBonusComposer(_MAX_CAPACITY, nyBonusSortOrder, getNYAwardsPacker())
        return formatter.getFormattedBonuses(bonuses, AWARDS_SIZES.BIG)

    def __onClose(self):
        self.__onCloseAction()

    def __onCloseAction(self):
        self.destroyWindow()


class NewYearStyleRewardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(NewYearStyleRewardWindow, self).__init__(content=NewYearStyleRewardView(*args, **kwargs), layer=WindowLayer.OVERLAY)
