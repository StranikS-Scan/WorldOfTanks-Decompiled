# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/mode_selector/fun_sub_selector_view.py
import logging
import typing
from fun_random_common.fun_constants import UNKNOWN_EVENT_ID, DEFAULT_ASSETS_PACK
from adisp import adisp_process
from battle_modifiers_ext.constants_ext import ClientDomain
from frameworks.wulf import ViewFlags, ViewSettings, ViewStatus
from fun_random.gui.feature.fun_constants import FunSubModesState
from fun_random.gui.feature.models.common import FunSubModesStatus
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunProgressionWatcher, FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression, hasMultipleSubModes, avoidSubModesStates
from fun_random.gui.impl.gen.view_models.views.lobby.feature.mode_selector.fun_random_sub_selector_card_model import FunRandomSubSelectorCardModel, CardState
from fun_random.gui.impl.gen.view_models.views.lobby.feature.mode_selector.fun_random_sub_selector_model import FunRandomSubSelectorModel
from fun_random.gui.impl.lobby.common.fun_view_helpers import getFormattedTimeLeft, getConditionText, packProgressionConditions, packInfiniteProgressionState, packInfiniteProgressionStage, packInfiniteProgressionConditions
from fun_random.gui.impl.lobby.common.fun_view_helpers import packAdditionalRewards, packProgressionActiveStage, packProgressionState, defineProgressionStatus
from fun_random.gui.impl.lobby.tooltips.fun_random_domain_tooltip_view import FunRandomDomainTooltipView
from fun_random.gui.impl.lobby.tooltips.fun_random_loot_box_tooltip_view import FunRandomLootBoxTooltipView
from fun_random.gui.impl.lobby.tooltips.fun_random_progression_tooltip_view import FunRandomProgressionTooltipView
from fun_random.gui.impl.lobby.tooltips.fun_random_reward_box_tooltip_views import NearestAdditionalRewardsTooltip
from gui.impl import backport
from gui.impl.auxiliary.tooltips.simple_tooltip import createSimpleTooltip
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.tooltips.mode_selector_tooltips_constants import ModeSelectorTooltipsConstants
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.shared import events, g_eventBus
from gui.shared.events import ModeSubSelectorEvent, FullscreenModeSelectorEvent
from helpers import dependency, time_utils
from shared_utils import findFirst
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from frameworks.wulf import View, Window, Array
    from frameworks.wulf.view.view_event import ViewEvent
    from fun_random.gui.feature.sub_modes.base_sub_mode import IFunSubMode
    from gui.impl.backport import TooltipData
_logger = logging.getLogger(__name__)
_SUB_MODE_CARD_STATE_MAP = {FunSubModesState.AFTER_SEASON: CardState.FINISHED,
 FunSubModesState.BEFORE_SEASON: CardState.NOT_STARTED,
 FunSubModesState.BETWEEN_SEASONS: CardState.NOT_STARTED,
 FunSubModesState.NOT_AVAILABLE_END: CardState.ACTIVE,
 FunSubModesState.NOT_AVAILABLE: CardState.ACTIVE,
 FunSubModesState.AVAILABLE: CardState.ACTIVE}

class FunModeSubSelectorView(ViewImpl, FunAssetPacksMixin, FunSubModesWatcher, FunProgressionWatcher):
    __slots__ = ('__tooltips',)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID=layoutID, flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=FunRandomSubSelectorModel())
        self.__tooltips = {}
        super(FunModeSubSelectorView, self).__init__(settings)
        g_eventBus.handleEvent(ModeSubSelectorEvent(ModeSubSelectorEvent.CHANGE_VISIBILITY, ctx={'visible': True}))

    @property
    def viewModel(self):
        return super(FunModeSubSelectorView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(FunModeSubSelectorView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipID = event.getArgument('tooltipId')
        if tooltipID == ModeSelectorTooltipsConstants.FUN_RANDOM_CALENDAR_TOOLTIP:
            subMode = self.__getSubModeByEvent(event)
            if subMode is not None:
                return self.__createBackportTooltip(backport.createTooltipData(isSpecial=True, specialAlias=tooltipID, specialArgs=(subMode.getSubModeID(),)))
            return
        elif tooltipID == ModeSelectorTooltipsConstants.DISABLED_TOOLTIP:
            subMode = self.__getSubModeByEvent(event)
            if subMode is not None and subMode.isFrozen():
                return createSimpleTooltip(self.getParentWindow(), event, body=backport.text(R.strings.fun_random.modeSubSelector.disabledCard.tooltip.body()))
            return
        else:
            return None if tooltipID is None else self.__tooltips.get(tooltipID)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.fun_random.lobby.tooltips.FunRandomProgressionTooltipView():
            return FunRandomProgressionTooltipView()
        elif contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            progression, showCount = self.getActiveProgression(), int(event.getArgument('showCount'))
            stageIdx = progression.activeStage.stageIndex if progression else -1
            packedRewards = packAdditionalRewards(progression, stageIdx, showCount, True) if progression else []
            if packedRewards:
                return NearestAdditionalRewardsTooltip(packedRewards)
            return
        elif contentID == R.views.battle_modifiers.lobby.tooltips.ModifiersDomainTooltipView():
            subModeID = int(event.getArgument('subModeId', UNKNOWN_EVENT_ID))
            modifiersDomain = event.getArgument('modifiersDomain', ClientDomain.UNDEFINED)
            return FunRandomDomainTooltipView(modifiersDomain, subModeID)
        elif contentID == R.views.fun_random.lobby.tooltips.FunRandomLootBoxTooltipView():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = None if tooltipId is None else self.__tooltips.get(tooltipId)
            lootboxID = tooltipData.specialArgs[0] if tooltipData and tooltipData.specialArgs else None
            if lootboxID:
                return FunRandomLootBoxTooltipView(lootboxID)
            return
        else:
            return super(FunModeSubSelectorView, self).createToolTipContent(event, contentID)

    def abortSelection(self):
        self.__onAbortSelection()
        self.destroyWindow()

    def closeSelection(self):
        self.__removeSelectorListeners()
        g_eventBus.handleEvent(events.DestroyGuiImplViewEvent(R.views.lobby.mode_selector.ModeSelectorView()))

    def setDisabledProgression(self, model=None):
        model = model or self.viewModel
        model.state.setStatus(defineProgressionStatus(None))
        return

    def _onLoading(self, *args, **kwargs):
        super(FunModeSubSelectorView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__invalidate(self.getSubModesStatus())

    def _finalize(self):
        self.__tooltips.clear()
        self.__removeListeners()
        g_eventBus.handleEvent(ModeSubSelectorEvent(ModeSubSelectorEvent.CHANGE_VISIBILITY, ctx={'visible': False}))
        super(FunModeSubSelectorView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClosed, self.closeSelection),
         (self.viewModel.onBackBtnClicked, self.__onAbortSelection),
         (self.viewModel.onInfoClicked, self.__onShowSubInfoPage),
         (self.viewModel.onItemClicked, self.__onSelectSubMode))

    def __addListeners(self):
        self.startSubSettingsListening(self.__invalidateAll)
        self.startSubStatusListening(self.__invalidateAll, tickMethod=self.__invalidateSubModesTimer)
        self.startProgressionListening(self.__invalidateProgression, tickMethod=self.__invalidateProgressionTimer)
        g_eventBus.addListener(FullscreenModeSelectorEvent.NAME, self.__onModeSelectorClosed)

    def __removeListeners(self):
        self.stopSubSettingsListening(self.__invalidateAll)
        self.stopSubStatusListening(self.__invalidateAll, tickMethod=self.__invalidateSubModesTimer)
        self.stopProgressionListening(self.__invalidateProgression, tickMethod=self.__invalidateProgressionTimer)
        self.__removeSelectorListeners()

    def __removeSelectorListeners(self):
        g_eventBus.removeListener(FullscreenModeSelectorEvent.NAME, self.__onModeSelectorClosed)

    def __getSubModeByEvent(self, event):
        assetsPointer = event.getArgument('modeName', DEFAULT_ASSETS_PACK)
        return findFirst(lambda sm: sm.getAssetsPointer() == assetsPointer, self.getSubModes())

    def __getSubModeStartDelta(self, status):
        return time_utils.getTimeDeltaFromNowInLocal(status.rightBorder) if status.state in FunSubModesState.BEFORE_STATES else 0

    def __getSubModeEndDelta(self, status):
        return getFormattedTimeLeft(time_utils.getTimeDeltaFromNowInLocal(status.rightBorder)) if status.state in FunSubModesState.INNER_STATES else ''

    def __createBackportTooltip(self, tooltipData):
        window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
        window.load()
        return window

    def __createCardModel(self, subMode, selectedSubModeID):
        subModeID = subMode.getSubModeID()
        card = FunRandomSubSelectorCardModel()
        card.setSubModeId(subModeID)
        card.setAssetsPointer(subMode.getAssetsPointer())
        card.setIsSelected(subModeID == selectedSubModeID)
        card.setConditions(getConditionText(subMode.getLocalsResRoot().subModeCard, subMode.getSettings().filtration.levels))
        status = self.getSubModesStatus(subModesIDs=[subModeID])
        card.setState(_SUB_MODE_CARD_STATE_MAP.get(status.state, CardState.DISABLED))
        card.setTimeToStart(self.__getSubModeStartDelta(status))
        card.setTimeLeft(self.__getSubModeEndDelta(status))
        isFrozen = status.state == FunSubModesState.SINGLE_FROZEN
        self._funRandomCtrl.notifications.markSeenAsFrozen([subModeID] if isFrozen else [])
        modifiersDomains = card.getModifiersDomains()
        for domain in subMode.getModifiersDataProvider().getDomains():
            modifiersDomains.addString(domain)

        modifiersDomains.invalidate()
        return card

    @adisp_process
    def __onSelectSubMode(self, args):
        self.__toggleSelectorClickProcessing(True)
        navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if not navigationPossible:
            self.__toggleSelectorClickProcessing(False)
            return
        result = yield self.selectFunRandomBattle(int(args.get('subModeId', UNKNOWN_EVENT_ID)))
        self.__toggleSelectorClickProcessing(False)
        if result and self.viewStatus == ViewStatus.LOADED:
            self.closeSelection()

    def __onShowSubInfoPage(self, args):
        self.showSubModeInfoPage(int(args.get('subModeId', UNKNOWN_EVENT_ID)))

    def __onModeSelectorClosed(self, event):
        if event is not None and not event.ctx.get('showing', False):
            self.abortSelection()
        return

    def __onAbortSelection(self, *_):
        self.__removeSelectorListeners()
        g_eventBus.handleEvent(ModeSubSelectorEvent(ModeSubSelectorEvent.CHANGE_VISIBILITY, ctx={'visible': False}))

    def __invalidate(self, status):
        with self.viewModel.transaction() as model:
            model.setAssetsPointer(self.getModeAssetsPointer())
            self.__invalidateSubModesCards(model.getCardList())
            if status.state in FunSubModesState.INNER_STATES:
                self.__fillProgression(model)
            else:
                self.setDisabledProgression(model)

    @hasMultipleSubModes(abortAction='abortSelection')
    @avoidSubModesStates(states=FunSubModesState.HIDDEN_SELECTOR_STATES, abortAction='abortSelection')
    def __invalidateAll(self, status, *_):
        self.__invalidate(status)

    @hasActiveProgression(abortAction='setDisabledProgression')
    def __invalidateProgression(self, *_):
        with self.viewModel.transaction() as model:
            self.__fillProgression(model)

    @hasActiveProgression()
    def __invalidateProgressionTimer(self, *_):
        self.viewModel.state.setStatusTimer(self.getActiveProgression().statusTimer)

    @hasMultipleSubModes()
    def __invalidateSubModesCards(self, cards):
        cards.clear()
        subMode = self._funRandomCtrl.subModesHolder.getDesiredSubMode()
        selectedSubModeID = subMode.getSubModeID() if subMode and subMode.isAvailable() else UNKNOWN_EVENT_ID
        for subMode in self.getSubModes(isOrdered=True):
            cards.addViewModel(self.__createCardModel(subMode, selectedSubModeID))

        cards.invalidate()

    def __invalidateSubModesTimer(self, *_):
        with self.viewModel.transaction() as model:
            self.__invalidateSubModesCards(model.getCardList())

    @hasActiveProgression(abortAction='setDisabledProgression')
    def __fillProgression(self, model):
        self.__tooltips.clear()
        progression = self.getActiveProgression()
        if progression.isInUnlimitedProgression:
            packInfiniteProgressionState(progression, model.state)
            packInfiniteProgressionStage(progression, model.currentStage, tooltips=self.__tooltips)
            packInfiniteProgressionConditions(progression, model.condition)
        else:
            packProgressionState(progression, model.state)
            packProgressionConditions(progression, model.condition)
            packProgressionActiveStage(progression, model.currentStage, tooltips=self.__tooltips)

    def __toggleSelectorClickProcessing(self, isClickProcessing):
        ctx = {'isClickProcessing': isClickProcessing}
        g_eventBus.handleEvent(ModeSubSelectorEvent(ModeSubSelectorEvent.CLICK_PROCESSING, ctx=ctx))
