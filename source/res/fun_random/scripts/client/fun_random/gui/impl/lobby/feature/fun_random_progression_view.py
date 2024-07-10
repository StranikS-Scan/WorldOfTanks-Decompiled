# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_progression_view.py
import BigWorld
import math_utils
from account_helpers.AccountSettings import AccountSettings, FUN_RANDOM_PROGRESSION_OPENED, FUN_RANDOM_PROGRESSION, FUN_RANDOM_PROGR_PREV_COUNTER, FUN_RANDOM_INF_PROGR_PREV_COUNTER, FUN_RANDOM_INF_PROGR_PREV_COMPLETE_COUNT
from frameworks.wulf import ViewFlags, ViewSettings
from fun_random.gui.feature.fun_sounds import FUN_PROGRESSION_SOUND_SPACE
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunProgressionWatcher, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_progression_view_model import FunRandomProgressionViewModel
from fun_random.gui.impl.lobby.common.fun_view_helpers import packAdditionalRewards, packFullProgressionConditions, packProgressionStages, packProgressionState, packInfiniteProgressionStage, packFullInfiniteProgressionConditions
from fun_random.gui.impl.lobby.tooltips.fun_random_loot_box_tooltip_view import FunRandomLootBoxTooltipView
from fun_random.gui.shared.event_dispatcher import showFunRandomTierList
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_types import LootBoxCompensationTooltipTypes
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showHangar
_DESTROY_ACTION_NAME = 'showHangar'

class FunRandomProgressionView(ViewImpl, LobbyHeaderVisibility, FunAssetPacksMixin, FunProgressionWatcher, FunSubModesWatcher):
    __slots__ = ('__tooltips',)
    _COMMON_SOUND_SPACE = FUN_PROGRESSION_SOUND_SPACE

    def __init__(self, *_, **__):
        settings = ViewSettings(layoutID=R.views.fun_random.lobby.feature.FunRandomProgression(), flags=ViewFlags.LOBBY_SUB_VIEW, model=FunRandomProgressionViewModel())
        self.__tooltips = {}
        self.__saveProgressCallbackId = None
        super(FunRandomProgressionView, self).__init__(settings)
        return

    @staticmethod
    def showHangar(*_):
        showHangar()

    @property
    def viewModel(self):
        return super(FunRandomProgressionView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(FunRandomProgressionView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            progression = self.getActiveProgression()
            showCount, stageIdx = int(event.getArgument('showCount')), int(event.getArgument('stageIdx'))
            packedRewards = packAdditionalRewards(progression, stageIdx, showCount) if progression else []
            if packedRewards:
                return AdditionalRewardsTooltip(packedRewards)
            return
        elif contentID == R.views.fun_random.lobby.tooltips.FunRandomLootBoxTooltipView():
            tooltipData = self.getTooltipData(event)
            lootboxID = tooltipData.specialArgs[0] if tooltipData and tooltipData.specialArgs else None
            if lootboxID:
                return FunRandomLootBoxTooltipView(lootboxID)
            return
        else:
            tooltipId = event.getArgument('tooltipId')
            tc = R.views.lobby.awards.tooltips.RewardCompensationTooltip()
            if event.contentID == tc:
                if tooltipId in self.__tooltips:
                    tooltipData = {'iconBefore': event.getArgument('iconBefore', ''),
                     'labelBefore': event.getArgument('labelBefore', ''),
                     'iconAfter': event.getArgument('iconAfter', ''),
                     'labelAfter': event.getArgument('labelAfter', ''),
                     'bonusName': event.getArgument('bonusName', ''),
                     'countBefore': event.getArgument('countBefore', 1),
                     'tooltipType': LootBoxCompensationTooltipTypes.VEHICLE}
                    tooltipData.update(self.__tooltips[tooltipId].specialArgs)
                    settings = ViewSettings(tc, model=LootBoxVehicleCompensationTooltipModel(), kwargs=tooltipData)
                    return VehicleCompensationTooltipContent(settings)
            return super(FunRandomProgressionView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def showInfoPage(self, *_):
        self.showCommonInfoPage()

    def _showTierList(self, *_):
        showFunRandomTierList()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.showHangar), (self.viewModel.onShowInfo, self.showInfoPage), (self.viewModel.onOpenTierList, self._showTierList))

    def _initialize(self, *args, **kwargs):
        super(FunRandomProgressionView, self)._initialize(*args, **kwargs)
        self.suspendLobbyHeader(self.uniqueID)

    def _finalize(self):
        self.__tooltips.clear()
        self.resumeLobbyHeader(self.uniqueID)
        self.stopProgressionListening(self.__invalidateAll, tickMethod=self.__invalidateTimer)
        if self.__saveProgressCallbackId is not None:
            BigWorld.cancelCallback(self.__saveProgressCallbackId)
            self.__saveProgress()
        super(FunRandomProgressionView, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(FunRandomProgressionView, self)._onLoading(*args, **kwargs)
        self.startProgressionListening(self.__invalidateAll, tickMethod=self.__invalidateTimer)
        self.__invalidateAll()

    @hasActiveProgression(abortAction=_DESTROY_ACTION_NAME)
    def __invalidateAll(self, *_):
        self.__tooltips.clear()
        progression = self.getActiveProgression()
        with self.viewModel.transaction() as model:
            settingsKey = FUN_RANDOM_PROGRESSION_OPENED
            wasOpened = AccountSettings.getSettings(settingsKey)
            model.setAssetsPointer(self.getModeAssetsPointer())
            model.setIsFirstOpen(not wasOpened)
            modeName = self.getModeUserName()
            packProgressionState(progression, model.state)
            packProgressionStages(progression, model.getStages(), self.__tooltips)
            packFullProgressionConditions(modeName, progression, model.condition)
            if progression.hasUnlimitedProgression:
                packInfiniteProgressionStage(progression, model.infiniteStage, tooltips=self.__tooltips)
                packFullInfiniteProgressionConditions(modeName, progression, model.infiniteCondition)
            if self.__saveProgressCallbackId is not None:
                BigWorld.cancelCallback(self.__saveProgressCallbackId)
            self.__saveProgressCallbackId = BigWorld.callback(1.0, self.__saveProgress)
            if not wasOpened:
                AccountSettings.setSettings(settingsKey, True)
        return

    @hasActiveProgression(abortAction=_DESTROY_ACTION_NAME)
    def __invalidateTimer(self, *_):
        self.viewModel.condition.setStatusTimer(self.getActiveProgression().statusTimer)

    def __saveProgress(self):
        self.__saveProgressCallbackId = None
        progression = self.getActiveProgression()
        if progression:
            pName = progression.config.name
            progressionsData = AccountSettings.getSettings(FUN_RANDOM_PROGRESSION)
            progressionCounters = progressionsData.get(pName, {})
            progressionCounters[FUN_RANDOM_PROGR_PREV_COUNTER] = math_utils.clamp(0, progression.conditions.maximumCounter, progression.conditions.counter)
            if progression.hasUnlimitedProgression:
                progressionCounters[FUN_RANDOM_INF_PROGR_PREV_COUNTER] = math_utils.clamp(0, progression.unlimitedProgression.maximumCounter, progression.unlimitedProgression.counter)
                completeCount = progression.unlimitedProgression.unlimitedExecutor.getBonusCount()
                progressionCounters[FUN_RANDOM_INF_PROGR_PREV_COMPLETE_COUNT] = completeCount
            progressionsData[pName] = progressionCounters
            AccountSettings.setSettings(FUN_RANDOM_PROGRESSION, progressionsData)
        return
