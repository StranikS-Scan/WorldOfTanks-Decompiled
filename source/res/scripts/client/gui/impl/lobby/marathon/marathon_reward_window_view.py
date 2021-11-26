# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/marathon/marathon_reward_window_view.py
import typing
import constants
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.marathon.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.marathon.marathon_prize_reward_model import MarathonPrizeRewardModel
from gui.impl.pub import ViewImpl
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from frameworks.wulf import Array, ViewSettings, ViewFlags
from gui.marathon.marathon_event import MarathonEvent
from gui.server_events.bonuses import splitBonuses
from gui.shared.event_dispatcher import showStylePreview, showHangar, selectVehicleInHangar
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.money import Currency
from helpers import dependency
from constants import IS_CHINA
from ids_generators import SequenceIDGenerator
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IMarathonEventsController
from skeletons.gui.server_events import IEventsCache
from gui.impl.lobby.marathon.marathon_reward_helper import getRewardImage, getRewardLabel, getRewardOverlayType
from gui.server_events.awards_formatters import getMarathonRewardScreenPacker
from gui.impl.lobby.marathon.marathon_reward_tooltip_content import MarathonRewardTooltipContent
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()
_ICON_PATH = R.images.gui.maps.icons.marathon.rewardWindow
REWARDS_PRIORITY = ('vehicles',
 'tankmen',
 constants.PREMIUM_ENTITLEMENTS.PLUS,
 'optionalDevice',
 Currency.CREDITS,
 'slots',
 'battleBooster',
 'crewBooks',
 'goodies',
 'equipment')
MAX_REWARDS_COUNT = 9

class MarathonRewardWindowView(ViewImpl):
    eventsCache = dependency.descriptor(IEventsCache)
    marathonController = dependency.descriptor(IMarathonEventsController)
    c11n = dependency.descriptor(ICustomizationService)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.marathon.RewardWindow())
        settings.flags = ViewFlags.VIEW
        settings.model = MarathonPrizeRewardModel()
        super(MarathonRewardWindowView, self).__init__(settings, *args, **kwargs)
        self.__rewards = []
        self.__convertRewards(ctx)
        self.__marathon = self.marathonController.getMarathon(ctx.get('marathonPrefix'))
        self.__idGen = SequenceIDGenerator()
        self.__bonusCache = {}

    @property
    def viewModel(self):
        return super(MarathonRewardWindowView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.marathon.tooltips.RestRewardTooltip() and len(self.__rewards) > MAX_REWARDS_COUNT:
            restRewards = self.__rewards[MAX_REWARDS_COUNT:]
            formatterRewards = self.__formatterRewards(restRewards, False)
            return MarathonRewardTooltipContent(formatterRewards)
        return super(MarathonRewardWindowView, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        tooltipId = event.getArgument('tooltipId')
        if not tooltipId:
            return super(MarathonRewardWindowView, self).createToolTip(event)
        bonus = self.__bonusCache.get(tooltipId)
        if bonus:
            window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs), self.getParentWindow())
            window.load()
            return window
        return super(MarathonRewardWindowView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(MarathonRewardWindowView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self._fillModel(model)

    def _initialize(self, *args, **kwargs):
        super(MarathonRewardWindowView, self)._initialize(*args, **kwargs)
        self._addListeners()

    def _finalize(self):
        self._removeListeners()
        self.__bonusCache.clear()
        super(MarathonRewardWindowView, self)._finalize()

    def _addListeners(self):
        self.viewModel.onAcceptClicked += self._onAccepted
        self.viewModel.onCancelClicked += self._onCancel
        self.viewModel.onSecondaryClicked += self._onSecondary

    def _removeListeners(self):
        self.viewModel.onAcceptClicked -= self._onAccepted
        self.viewModel.onCancelClicked -= self._onCancel
        self.viewModel.onSecondaryClicked += self._onSecondary

    def _getVehicleObtainedTitle(self):
        current, last = self.__marathon.getMarathonProgress()
        if current == 0:
            return R.strings.marathon.reward.stageAllComplete()
        return R.strings.marathon.reward.stageNotAllComplete() if current < last else R.strings.marathon.reward.stageCompleteLast()

    def _fillModel(self, model):
        isMainProgressionReward = not self.__marathon.isPostRewardObtained()
        vehicle = self.__marathon.vehicle
        self._fillRewards(model)
        if isMainProgressionReward:
            stage = 1
            suptitle = self._getVehicleObtainedTitle()
            model.setSupTitle(suptitle)
            model.setTitle(R.strings.marathon.reward.vehicleTitle())
            model.setSubTitle(R.strings.marathon.reward.nameVehicle())
            model.setImage(_ICON_PATH.vehicle_image_cn() if IS_CHINA else _ICON_PATH.vehicle_image())
            model.vehicle.setName(vehicle.userName)
            model.vehicle.setType(vehicle.type)
            model.vehicle.setLevel(vehicle.level)
        else:
            stage = 2
            model.setSupTitle(R.strings.marathon.reward.stageStyle())
            model.setTitle(R.strings.marathon.reward.styleTitle())
            model.setSubTitle(R.strings.marathon.reward.nameStyle())
            model.setImage(_ICON_PATH.style_image_cn() if IS_CHINA else _ICON_PATH.style_image())
            model.setIconReward(_ICON_PATH.style_reward())
        model.setHasVehicle(isMainProgressionReward)
        model.setStage(stage)

    def _onAccepted(self, *args):
        self.destroyWindow()
        if not self.__marathon.isPostRewardObtained():
            selectVehicleInHangar(self.__marathon.vehicle.compactDescr)

    def _onCancel(self):
        self.destroyWindow()

    def _onSecondary(self):
        if self.__marathon.vehicle.isInInventory:
            self.c11n.showCustomization(self.__marathon.vehicle.invID)
        else:
            style = self.c11n.getItemByID(GUI_ITEM_TYPE.STYLE, self.__marathon.styleID)
            showStylePreview(self.__marathon.vehicle.compactDescr, style, style.getDescription(), showHangar)

    def _fillRewards(self, model):
        rewardsCount = len(self.__rewards)
        if rewardsCount > MAX_REWARDS_COUNT:
            rewards = self.__rewards[:MAX_REWARDS_COUNT]
            restRewardsCount = rewardsCount - MAX_REWARDS_COUNT
            model.setRewards(self.__formatterRewards(rewards, True))
            model.setRestRewardsCount(restRewardsCount)
        else:
            model.setRewards(self.__formatterRewards(self.__rewards, True))
            model.setRestRewardsCount(0)

    def __formatterRewards(self, rewards, addTooltip=False):
        results = Array()
        for reward in rewards:
            model = BonusModel()
            model.setName(reward.bonusName)
            model.setIcon(getRewardImage(reward.images['big']))
            model.setLabel(getRewardLabel(reward.label))
            model.setOverlayType(getRewardOverlayType(reward.overlayType))
            if addTooltip:
                self.__setTooltip(model, reward)
            else:
                model.setDescription(reward.userName)
            results.addViewModel(model)

        return results

    def __setTooltip(self, model, reward):
        tooltipId = '{}'.format(self.__idGen.next())
        self.__bonusCache[tooltipId] = reward
        model.setTooltipId(tooltipId)

    def __sortRewardsByPriority(self, rewards, priority=REWARDS_PRIORITY, defaultPriority=len(REWARDS_PRIORITY)):
        rewards.sort(key=lambda x: self.__sortRewardsFunc(x, priority, defaultPriority))
        return rewards

    def __sortRewardsFunc(self, bonus, priority, defaultPriority):
        name = bonus.getName()
        if name == 'items':
            epicBonusList = bonus.getWrappedEpicBonusList()
            if epicBonusList:
                id_ = epicBonusList[0]['id']
                name = self.itemsCache.items.getItemByCD(id_).itemTypeName
        return priority.index(name) if name in priority else defaultPriority

    def __convertRewards(self, ctx):
        self.__rewards = ctx.get('rewards', [])
        self.__rewards = splitBonuses(self.__rewards)
        crewRewards = ctx.get('crewRewards', None)
        if crewRewards:
            self.__rewards.append(crewRewards)
        self.__rewards = self.__sortRewardsByPriority(self.__rewards)
        formatter = getMarathonRewardScreenPacker()
        self.__rewards = formatter.format(self.__rewards)
        return
