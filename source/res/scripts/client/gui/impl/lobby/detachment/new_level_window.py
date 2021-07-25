# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/new_level_window.py
from functools import partial
from itertools import izip
import typing
from crew2.settings_globals import g_commanderSettings
from frameworks.wulf import ViewSettings, View
from gui.impl import backport
from gui.impl.auxiliary.detachment_helper import fillDetachmentShortInfoModel
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.new_level_rewards_constants import NewLevelRewardsConstants
from gui.impl.gen.view_models.views.lobby.detachment.new_level_window_model import NewLevelWindowModel
from gui.impl.lobby.detachment.navigation_view_impl import NavigationViewImpl
from gui.impl.lobby.detachment.rewards import REWARD_TYPES, TRAINING
from gui.impl.lobby.detachment.tooltips.colored_simple_tooltip import ColoredSimpleTooltip
from gui.impl.lobby.detachment.tooltips.progression_discount_tooltip import ProgressionDiscountTooltip
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.tooltips.points_info_tooltip_view import PointInfoTooltipView
from gui.impl.lobby.detachment.tooltips.rank_tooltip import RankTooltip
from gui.impl.pub.dialog_window import DialogFlags
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.badges import buildBadge
from gui.shared.event_dispatcher import showDetachmentViewById
from helpers import dependency
from items.components.detachment_constants import RewardTypes
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from sound_constants import HANGAR_OVERLAY_SOUND_SPACE
from uilogging.detachment.loggers import DetachmentLogger
from uilogging.detachment.constants import GROUP, ACTION
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent
    from gui.shared.gui_items.badge import Badge
    from gui.shared.gui_items.detachment import Detachment
    from gui.impl.lobby.detachment.rewards import BaseReward
_NEW_LEVEL_SOUND = 'detachment_new_level'
_BASIC_LEVEL = 100

def _progressionDiscountTooltip(detachment, event):
    discountType = event.getArgument('extraValue')
    discount = int(event.getArgument('value'))
    dynAcc = R.strings.tooltips.progressionDiscount.dyn(discountType)
    header = backport.text(dynAcc.title())
    body = backport.text(dynAcc.body())
    if discountType == TRAINING:
        note = backport.text(dynAcc.body2(), icon='%(info)', minTier=1, maxTier=detachment.progression.firstPaidSpecializationLevel - 1)
        return ColoredSimpleTooltip(header, body, note)
    return ProgressionDiscountTooltip(header, body, backport.text(R.strings.tooltips.progressionDiscount.learningHelp()), str(-discount))


def _createRankTooltip(event):
    nationID = int(event.getArgument('value'))
    rank = event.getArgument('extraValue')
    record = g_commanderSettings.ranks.getRankRecord(nationID, rank)
    return RankTooltip(record)


def _createVehicleSlotTooltip(detachment, _):
    levelsUnlock = {}
    if detachment:
        keysInLocal = ('firstNumber', 'secondNumber')
        for key, value in izip(keysInLocal, detachment.getVehicleSlotUnlockLevels()[1:]):
            levelsUnlock[key] = value

    return ColoredSimpleTooltip(backport.text(R.strings.tooltips.detachment.vehicleSlotReward.header()), backport.text(R.strings.tooltips.detachment.vehicleSlotReward.body(), **levelsUnlock))


def _createMasteryTooltip(event):
    value = int(event.getArgument('value'))
    extraValue = int(event.getArgument('extraValue'))
    return ColoredSimpleTooltip(backport.text(R.strings.tooltips.detachment.masteryReward.header()), backport.text(R.strings.tooltips.detachment.masteryReward.body(), basicNumber=_BASIC_LEVEL + extraValue, currentNumber=value))


def _createBadgeTooltip(event):
    badgeID = int(event.getArgument('value'))
    badge = buildBadge(badgeID)
    return ColoredSimpleTooltip(badge.getUserName(), badge.getUserDescription())


class NewLevelWindowView(NavigationViewImpl):
    __slots__ = ('_detInvID', '_detachment', '_oldDetachment', '_accountBadgeLevel', '_tooltipFactories')
    detachmentCache = dependency.descriptor(IDetachmentCache)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)
    _COMMON_SOUND_SPACE = HANGAR_OVERLAY_SOUND_SPACE
    _REWARDS_ORDER = (RewardTypes.RANK,
     RewardTypes.BADGE_LEVEL,
     RewardTypes.SKILL_POINTS,
     RewardTypes.AUTO_PERKS,
     RewardTypes.SCHOOL_DISCOUNT,
     RewardTypes.ACADEMY_DISCOUNT,
     RewardTypes.VEHICLE_SLOTS,
     RewardTypes.INSTRUCTOR_SLOTS)
    uiLogger = DetachmentLogger(GROUP.NEW_DETACHMENT_LEVEL)

    def __init__(self, layoutID, detInvID, detCompDescr, oldDetCompDescr, skinID, navigationViewSettings, accountBadgeLevel=0):
        settings = ViewSettings(layoutID)
        settings.model = NewLevelWindowModel()
        self._detInvID = detInvID
        self._accountBadgeLevel = accountBadgeLevel
        if detCompDescr:
            self._detachment = self.itemsFactory.createDetachment(detCompDescr, proxy=self.detachmentCache, invID=detInvID, skinID=skinID)
        else:
            self._detachment = self.detachmentCache.getDetachment(detInvID)
        self._oldDetachment = self.itemsFactory.createDetachment(oldDetCompDescr) if oldDetCompDescr else None
        super(NewLevelWindowView, self).__init__(settings, ctx={'navigationViewSettings': navigationViewSettings})
        self._tooltipFactories = {NewLevelRewardsConstants.RANK: _createRankTooltip,
         NewLevelRewardsConstants.BADGE: _createBadgeTooltip,
         NewLevelRewardsConstants.VEHICLE_PROFICIENCY: _createMasteryTooltip,
         NewLevelRewardsConstants.PROGRESSION_DISCOUNT: partial(_progressionDiscountTooltip, self._detachment),
         NewLevelRewardsConstants.VEHICLE_SLOT: partial(_createVehicleSlotTooltip, self._detachment),
         NewLevelRewardsConstants.INSTRUCTOR_SLOT: lambda _: getInstructorTooltip(detachment=self._detachment)}
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            rewardType = event.getArgument('type')
            createTooltip = self._tooltipFactories.get(rewardType)
            if createTooltip:
                return createTooltip(event)
        elif contentID == R.views.lobby.detachment.tooltips.PointsInfoTooltip():
            PointInfoTooltipView.uiLogger.setGroup(self.uiLogger.group)
            return PointInfoTooltipView(event.contentID, detachmentID=self._detInvID, freePoints=False)

    def _initModel(self, vm):
        super(NewLevelWindowView, self)._initModel(vm)
        self._fillModel(vm)

    def _initialize(self):
        super(NewLevelWindowView, self)._initialize()
        self.soundManager.playInstantSound(backport.sound(R.sounds.detachment_progress_bar_stop_all()))
        self.soundManager.playSound(_NEW_LEVEL_SOUND)
        self.uiLogger.startAction(ACTION.OPEN)

    def _finalize(self):
        self._tooltipFactories = {}
        self._detachment = None
        self.uiLogger.stopAction(ACTION.OPEN)
        super(NewLevelWindowView, self)._finalize()
        return

    def _addListeners(self):
        super(NewLevelWindowView, self)._addListeners()
        self.viewModel.onGoToBadges += self._goToBadges
        self.viewModel.onGoToPersonalCase += self.__goToPersonalCase

    def _removeListeners(self):
        self.viewModel.onGoToBadges -= self._goToBadges
        self.viewModel.onGoToPersonalCase -= self.__goToPersonalCase
        super(NewLevelWindowView, self)._removeListeners()

    def _goToBadges(self):
        from gui.shared.event_dispatcher import showBadges
        showBadges()

    def _fillModel(self, vm):
        self._fillRewards(vm.getRewardsList())
        vm.setEliteTitle(self._detachment.eliteTitle)
        fillDetachmentShortInfoModel(vm.detachmentInfo, self._detachment, fillInstructors=False)

    def _fillRewards(self, listModel):
        rewards = self._detachment.getRewardsDiff(self._oldDetachment, self._accountBadgeLevel)
        for rewardType in self._REWARDS_ORDER:
            rewardValue = rewards.get(rewardType)
            reward = REWARD_TYPES[rewardType](self._detachment, rewardValue, not bool(self._oldDetachment))
            if reward.model:
                listModel.addViewModel(reward.model)

        listModel.invalidate()

    def __goToPersonalCase(self):
        showDetachmentViewById(NavigationViewModel.PERSONAL_CASE_BASE, {'detInvID': self._detInvID})


class NewLevelWindow(LobbyNotificationWindow):
    __slots__ = ('_detInvID',)

    def __init__(self, detInvID, detCompDescr, oldDetCompDescr, skinID, navigationViewSettings, accountBadgeLevel=0, parent=None):
        super(NewLevelWindow, self).__init__(DialogFlags.TOP_FULLSCREEN_WINDOW, content=NewLevelWindowView(R.views.lobby.detachment.NewLevelWindow(), detInvID, detCompDescr, oldDetCompDescr, skinID, navigationViewSettings, accountBadgeLevel), parent=parent)
        self._detInvID = detInvID

    def isParamsEqual(self, detInvID, *args, **kwargs):
        return detInvID == self._detInvID
