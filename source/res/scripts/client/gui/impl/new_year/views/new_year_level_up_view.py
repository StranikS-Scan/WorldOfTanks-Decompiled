# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_level_up_view.py
import random
from functools import partial
from frameworks.wulf import ViewSettings
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import BonusNameQuestsBonusComposer, MERGED_BONUS_NAME
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport import TooltipData
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_level_up_view_model import NewYearLevelUpViewModel
from gui.impl.new_year.new_year_helper import nyBonusSortOrder
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyOverlay, OverlayBehavior, OverlayBehaviorFlags
from gui.server_events.awards_formatters import getNYAwardsPacker, AWARDS_SIZES, LABEL_ALIGN
from gui.impl.auxiliary.rewards_helper import getRewardRendererModelPresenter
from gui.impl.auxiliary.rewards_helper import VehicleCompensationModelPresenter, LootVehicleRewardPresenter
from gui.impl.new_year.tooltips.ny_talisman_tooltip import NewYearTalismanTooltipContent
from gui.impl.new_year.tooltips.new_year_tank_slot_tooltip import NewYearTankSlotTooltipContent
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxVideoStartStopHandler, LootBoxVideos, setOverlayHangarGeneral
from gui.server_events.recruit_helper import getRecruitInfo, DEFAULT_NY_GIRL
from gui.shared.event_dispatcher import showNewYearVehiclesView, showNYLevelUpWindow, showVideoView
from helpers import dependency, int2roman
from skeletons.new_year import INewYearController, ITalismanSceneController
_VEHICLES_BONUS_NAME = 'vehicles'
_TALISMAN_CAPACITY = 5
_MAX_CAPACITY = 6
_COMPENSATION_PRESENTERS = {_VEHICLES_BONUS_NAME: VehicleCompensationModelPresenter()}
_MODEL_PRESENTERS = {_VEHICLES_BONUS_NAME: LootVehicleRewardPresenter()}
_FIRST_LVL = 1

class NewYearLevelUpWindowContent(ViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    _talismanController = dependency.descriptor(ITalismanSceneController)
    __slots__ = ('__rewards', '__tooltipData', '__isFirstLevelUp', '__videoStartStopHandler')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_level_up_view.NewYearLevelUpView())
        settings.model = NewYearLevelUpViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearLevelUpWindowContent, self).__init__(settings)
        self.__tooltipData = {}
        self.__isFirstLevelUp = False
        self.__rewards = None
        self.__videoStartStopHandler = LootBoxVideoStartStopHandler()
        return

    @property
    def viewModel(self):
        return super(NewYearLevelUpWindowContent, self).getViewModel()

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.lobby.new_year.tooltips.ny_talisman_tooltip.NewYearTalismanTooltipContent():
            idx = int(event.getArgument('idx'))
            return NewYearTalismanTooltipContent(level=idx)
        return NewYearTankSlotTooltipContent(level=self.viewModel.getLevel(), levelName=self.viewModel.getLevelName()) if ctID == R.views.lobby.new_year.tooltips.new_year_tank_slot_tooltip.NewYearTankSlotTooltipContent() else super(NewYearLevelUpWindowContent, self).createToolTipContent(event, ctID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = None
            if tooltipId is not None:
                window = BackportTooltipWindow(self.__tooltipData[tooltipId], self.getParentWindow())
                window.load()
            return window
        else:
            return super(NewYearLevelUpWindowContent, self).createToolTip(event)

    def getRewards(self):
        return self.__rewards

    def appendRewards(self, ctx):
        for level, rewards in ctx.iteritems():
            self.__rewards[level] = rewards

    def _onLoading(self, ctx):
        super(NewYearLevelUpWindowContent, self)._onLoading()
        self.__isFirstLevelUp = _FIRST_LVL in ctx
        self.__rewards = ctx
        self.viewModel.onClose += self.__onClose
        self.viewModel.onToTanks += self.__onToTanks
        self.viewModel.onToTalismans += self.__onToTalismans
        if self.__rewards:
            self.__setRewards(*self.__rewards.popitem(last=False))

    def _initialize(self, *args, **kwargs):
        super(NewYearLevelUpWindowContent, self)._initialize(*args, **kwargs)
        setOverlayHangarGeneral(True)

    def _finalize(self):
        setOverlayHangarGeneral(False)
        super(NewYearLevelUpWindowContent, self)._finalize()
        self.__rewards = None
        self.getViewModel().onClose -= self.__onClose
        self.getViewModel().onToTanks -= self.__onToTanks
        self.getViewModel().onToTalismans -= self.__onToTalismans
        self.__videoStartStopHandler.onVideoDone()
        return

    def __onCloseAction(self, ignore=False):
        if self.__rewards and not ignore:
            self.__setRewards(*self.__rewards.popitem(last=False))
            return
        if self.__isFirstLevelUp:
            showVideoView(R.videos.lootboxes.ng_startup(), onVideoStartHandler=partial(self.__videoStartStopHandler.onVideoStart, videoId=LootBoxVideos.START), onVideoStopHandler=self.__onVideoDone)
        else:
            self.destroyWindow()

    def __onVideoDone(self):
        self.__videoStartStopHandler.onVideoDone()
        self.destroyWindow()

    def __onToTanks(self):
        rewards = self.__rewards
        self.destroyWindow()
        if rewards:
            showNewYearVehiclesView(backCtx=lambda : showNYLevelUpWindow(rewards))
        else:
            showNewYearVehiclesView()

    def __onToTalismans(self):
        self.__onCloseAction(ignore=True)
        self._talismanController.switchToPreview()

    def __onClose(self):
        self.__onCloseAction()

    def __onCollectRewards(self):
        self.__onCloseAction()

    def __setRewards(self, level, rewards):
        hasTalisman = self._nyController.getLevel(level).hasTalisman()
        allNotReceived = [ item.getSetting() for item in self._nyController.getTalismans() if not item.isInInventory() ]
        talismanSetting = random.choice(allNotReceived)
        rewards = self.__getRewards(rewards, hasTalisman)
        with self.getViewModel().transaction() as model:
            model.setLevel(level)
            model.setLevelName(int2roman(level))
            model.setContainsTalisman(hasTalisman)
            model.setTalismanSetting(talismanSetting)
            model.setHasVehicleBranch(self._nyController.getVehicleBranch().getSlotByLevel(level) is not None)
            rewardsList = model.getRewards()
            rewardsList.clear()
            for index, reward in enumerate(rewards):
                formatter = getRewardRendererModelPresenter(reward, _MODEL_PRESENTERS, _COMPENSATION_PRESENTERS)
                rewardRender = formatter.getModel(reward, index)
                rewardsList.addViewModel(rewardRender)
                self.__tooltipData[index] = TooltipData(tooltip=reward.get('tooltip', None), isSpecial=reward.get('isSpecial', False), specialAlias=reward.get('specialAlias', ''), specialArgs=reward.get('specialArgs', None))

            rewardsList.invalidate()
        return

    @classmethod
    def __getRewards(cls, bonuses, hasTalisman):
        capacity = _TALISMAN_CAPACITY if hasTalisman else _MAX_CAPACITY
        bonuses.sort(key=nyBonusSortOrder)
        formatter = BonusNameQuestsBonusComposer(displayedAwardsCount=capacity, awardsFormatter=getNYAwardsPacker())
        formattedBonuses = formatter.getFormattedBonuses(bonuses, AWARDS_SIZES.BIG)[::-1]
        if formattedBonuses and formattedBonuses[0].get('bonusName', '') == MERGED_BONUS_NAME:
            formattedBonuses[0]['label'] = ''
        if hasTalisman:
            formattedBonuses.append(_makeFakeLockedTankwomanFormattedBonus(size=AWARDS_SIZES.BIG))
        return formattedBonuses


class NewYearLevelUpOverlayBehavior(OverlayBehavior):
    __slots__ = ('__rewards',)
    __talismanCtrl = dependency.descriptor(ITalismanSceneController)

    def __init__(self):
        super(NewYearLevelUpOverlayBehavior, self).__init__(flags=OverlayBehaviorFlags.IS_EXCLUSIVE)
        self.__rewards = {}

    def close(self, window):
        self.__rewards = window.content.getRewards()
        if self.__rewards:
            self._flags |= OverlayBehaviorFlags.IS_REPEATABLE
        else:
            self._flags &= ~OverlayBehaviorFlags.IS_REPEATABLE

    def repeat(self):
        return NewYearLevelUpWindow(self.__rewards) if not self.__talismanCtrl.isInPreview() else None


class NewYearLevelUpWindow(LobbyOverlay):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(NewYearLevelUpWindow, self).__init__(behavior=NewYearLevelUpOverlayBehavior(), content=NewYearLevelUpWindowContent(*args, **kwargs))


def _makeFakeLockedTankwomanFormattedBonus(size):
    notRecruitedInfo = getRecruitInfo(DEFAULT_NY_GIRL)
    return {'label': '',
     'imgSource': backport.image(R.images.gui.maps.icons.quests.bonuses.dyn(size).dyn('lockedTankwoman')()),
     'tooltip': None,
     'isSpecial': True,
     'specialAlias': TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED,
     'specialArgs': [DEFAULT_NY_GIRL],
     'align': LABEL_ALIGN.CENTER,
     'userName': notRecruitedInfo.getFullUserName(),
     'hasCompensation': False,
     'compensationReason': None,
     'highlightType': None,
     'overlayType': None,
     'highlightIcon': None,
     'overlayIcon': None,
     'bonusName': 'tmanToken'}
