# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_guest_d_customization.py
import CGF
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_DOG_PAGE_VISITED
from cgf_components import hangar_camera_manager
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_guest_d_customization_model import ViewState, WidgetState
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.ny_sacks_model import NySacksModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.sack_model import SackModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.group_slots_model import GroupSlotsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.slot_model import SlotModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.toy_model import SlotType
from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import getLootboxBonuses, getNYSackRewardBonusPacker
from gui.impl.lobby.new_year.glade.ny_toys_list import NyToysList
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from gui.impl.lobby.new_year.tooltips.ny_decoration_unavailable_tooltip import NyDecorationUnavailableTooltip
from gui.impl.lobby.new_year.tooltips.ny_dog_decoration_tooltip import NyDogDecorationTooltip
from gui.impl.lobby.new_year.tooltips.ny_sacks_tooltip import NySacksTooltip
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.new_year_bonus_packer import packBonusModelAndTooltipData
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.event_dispatcher import showBundlePurchaseDialog
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from helpers.CallbackDelayer import CallbacksSetByID
from items.components.ny_constants import GUEST_D_SLOT_GROUPS, INVALID_TOY_ID
from new_year.celebrity.celebrity_quests_helpers import getDogLevel
from new_year.newyear_cgf_components.lobby_customization_components import LobbyCustomizableObjectsManager
from new_year.ny_constants import SyncDataKeys, GuestsQuestsTokens, NYObjects
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_model import NewYearChallengeModel
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_guest_d_customization_model import NewYearGuestDCustomizationModel
    from typing import Tuple, Callable
WIDGET_STATE_MAP = {-1: WidgetState.UNAVAILABLE,
 0: WidgetState.LEVEL2,
 1: WidgetState.LEVEL3,
 2: WidgetState.LEVEL4,
 3: WidgetState.ALLPURCHASED}
TIME_TILL_TO_HIDE_MARKER = 12.0
INFO_MARKER_ID = 1

class NyChallengeGuestDCustomization(NyHistoryPresenter):
    __slots__ = ('__toysList', '__blur', '__delayer')
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __SYNC_KEYS = {SyncDataKeys.INVENTORY_TOYS, SyncDataKeys.SLOTS, SyncDataKeys.OBJECTS_LEVELS}

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(NyChallengeGuestDCustomization, self).__init__(viewModel, parentView, soundConfig)
        self.__toysList = NyToysList()
        self.__blur = None
        self.__delayer = CallbacksSetByID()
        return

    @property
    def viewModel(self):
        model = self.getViewModel()
        return model.guestDCustomizationModel

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NySacksTooltip():
            return NySacksTooltip(event.getArgument('bundleType'))
        if contentID == R.views.lobby.new_year.tooltips.NyDecorationTooltip():
            toyID = event.getArgument('toyID')
            return NyDecorationTooltip(toyID)
        if contentID == R.views.lobby.new_year.tooltips.NyDecorationUnavailableTooltip():
            toyID = event.getArgument('toyID')
            return NyDecorationUnavailableTooltip(toyID)
        if contentID == R.views.lobby.new_year.tooltips.NyDogDecorationTooltip():
            toyID = event.getArgument('toyID')
            state = event.getArgument('state')
            return NyDogDecorationTooltip(toyID, state)
        return super(NyChallengeGuestDCustomization, self).createToolTipContent(event, contentID)

    def initialize(self, *args, **kwargs):
        super(NyChallengeGuestDCustomization, self).initialize(*args, **kwargs)
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__toysList.initialize(self.viewModel.toySlotsBar)
        if self.__hasDogToken():
            self.__delayer.delayCallback(INFO_MARKER_ID, TIME_TILL_TO_HIDE_MARKER, self.__hideInfoMarker)
        self.__subscribeCameraEvents(self.__getCameraEvents())
        with self.viewModel.transaction() as model:
            self.__updateSlots(fullUpdate=True, model=model)
            self.__updateMainState()
            self.__updateSacksEntryPoint()
            if self.__isCameraSwitched():
                self.__updateSacksVisible(True)
                self.__updateSacks()
            else:
                self.__updateSacksVisible(False)

    def finalize(self):
        super(NyChallengeGuestDCustomization, self).finalize()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__unsubscribeCameraEvents(self.__getCameraEvents())
        self.__toysList.finalize()
        self.__clearBlur()
        self.__delayer.clear()
        if self.__hasDogToken():
            self.__hideInfoMarker()

    @property
    def _cameraManager(self):
        return CGF.getManager(self.__hangarSpace.spaceID, hangar_camera_manager.HangarCameraManager) if self.__hangarSpace.spaceID is not None else None

    def _getEvents(self):
        return super(NyChallengeGuestDCustomization, self)._getEvents() + ((self.viewModel.toySlotsBar.onHoverSlot, self.__onHoverSlot),
         (self.viewModel.toySlotsBar.onHoverOutSlot, self.__onHoverOutSlot),
         (self.viewModel.toySlotsBar.onSelectSlot, self.__onSelectSlot),
         (self.viewModel.onOpenBuySacksScreen, self.__onOpenBuySacksScreen),
         (self.viewModel.onGoToGladeView, self.__onGoToGladeView),
         (self.viewModel.sacksModel.onOpenSack, self.__onOpenSack),
         (self.viewModel.sacksModel.onOpenAnimationEnd, self.__onOpenAnimationEnd),
         (self._nyController.onDataUpdated, self.__onDataUpdated),
         (self._nyController.onUpdateSlot, self.__onUpdateSlot),
         (self._nyController.sacksHelper.onSackOpened, self.__onSackOpened),
         (self._friendsService.onFriendHangarEnter, self.__updateSacks),
         (self._friendsService.onFriendHangarExit, self.__updateSacks),
         (self._nyController.sacksHelper.onUpdated, self.__updateSacks),
         (self._nyController.sacksHelper.onUpdated, self.__updateSacksEntryPoint))

    @classmethod
    def __subscribeCameraEvents(cls, handlers):
        for event, handler in handlers:
            event += handler

    @classmethod
    def __unsubscribeCameraEvents(cls, handlers):
        for event, handler in handlers:
            if event:
                event -= handler

    def __getCameraEvents(self):
        cameraEvents = tuple()
        cameraManager = self._cameraManager
        if cameraManager:
            cameraEvents += ((cameraManager.onCameraSwitched, self.__onCameraSwitched),)
        return cameraEvents

    def __onCameraSwitched(self, cameraName):
        if cameraName == NYObjects.CELEBRITY_D:
            self.__updateSacksVisible(True)
            self.__updateSacks()

    def __isCameraSwitched(self):
        cameraManager = self._cameraManager
        return cameraManager and cameraManager.getCurrentCameraName() == NYObjects.CELEBRITY_D and not cameraManager.isCameraSwitching()

    def __updateSacksVisible(self, visible=False):
        self.viewModel.sacksModel.setIsReady(visible)

    def __updateSacks(self, *args, **kwargs):
        if self.viewModel.sacksModel.getIsOpening():
            return
        with self.viewModel.sacksModel.transaction() as model:
            model.setMissionsCompleted(self._nyController.sacksHelper.getMissionsCompleted())
            model.setMissionsTotal(self._nyController.sacksHelper.getMissionsTotal())
            model.setMissionsCountdown(self._nyController.sacksHelper.getMissionsCountDown())
            model.setMissionDescription(self._nyController.sacksHelper.getMissionsDescription())
            sacks = model.getSacks()
            sacks.clear()
            for item in self._nyController.sacksHelper.getSacks():
                sack = SackModel()
                sack.setCount(item.count)
                sack.setLevel(item.level)
                sacks.addViewModel(sack)

            sacks.invalidate()

    def __updateSlots(self, fullUpdate, model):
        groups = GUEST_D_SLOT_GROUPS
        slotsData = self._itemsCache.items.festivity.getSlotsData()
        toys = self._itemsCache.items.festivity.getToys()
        actualLength = len(groups)
        currentLength = model.toySlotsBar.groupSlots.getItemsLength()
        if currentLength != actualLength:
            fullUpdate = True
            if actualLength > currentLength:
                for _ in range(actualLength - currentLength):
                    model.toySlotsBar.groupSlots.addViewModel(GroupSlotsModel())

            else:
                for _ in range(currentLength - actualLength):
                    model.toySlotsBar.groupSlots.removeItemByIndex(model.toySlotsBar.groupSlots.getItemsLength() - 1)

        slots = self._nyController.getSlotDescrs()
        for groupIdx, groupName in enumerate(groups):
            descrSlots = [ slot for slot in slots if slot.type == groupName ]
            groupModel = model.toySlotsBar.groupSlots.getItem(groupIdx)
            if fullUpdate:
                groupModel.slots.clear()
            for slotIdx, slotDescr in enumerate(descrSlots):
                toyID = slotsData[slotDescr.id]
                slotType = slotDescr.type
                if toyID == INVALID_TOY_ID:
                    icon = R.images.gui.maps.icons.newYear.decoration_types.craft.dyn(slotType)()
                    isEmpty = True
                else:
                    toy = toys[slotDescr.id][toyID]
                    icon = toy.getIcon()
                    isEmpty = False
                slot = SlotModel() if fullUpdate else groupModel.slots.getItem(slotIdx)
                slot.setSlotId(slotDescr.id)
                slot.setIsEmpty(isEmpty)
                slot.setToyId(toyID)
                slot.setIcon(icon)
                slot.setSlotType(SlotType.GUESTD.value)
                if fullUpdate:
                    groupModel.slots.addViewModel(slot)

        if fullUpdate:
            model.toySlotsBar.groupSlots.invalidate()

    def __updateSacksEntryPoint(self):
        dogLevel = getDogLevel()
        with self.viewModel.transaction() as model:
            model.setWidgetState(WIDGET_STATE_MAP[dogLevel])
            model.setHasWidgetMarker(self._nyController.isSacksMarkerShown())

    def __updateMainState(self):
        state = ViewState.ACTIVE if self._nyController.isTokenReceived(GuestsQuestsTokens.TOKEN_DOG) else ViewState.EMPTY
        if state == ViewState.EMPTY:
            self.__blur = CachedBlur(enabled=True, blurRadius=0.3)
        else:
            if not AccountSettings.getUIFlag(NY_DOG_PAGE_VISITED):
                AccountSettings.setUIFlag(NY_DOG_PAGE_VISITED, True)
                g_eventBus.handleEvent(events.NyDogEvent(events.NyDogEvent.DOG_PAGE_VISITED), scope=EVENT_BUS_SCOPE.LOBBY)
            self.__clearBlur()
        self.viewModel.setState(state)

    def __onHoverSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), True)

    def __onHoverOutSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), False)

    def __onSelectSlot(self, args):
        with self.viewModel.transaction() as model:
            selectedSlotId = int(args['slotId'])
            model.toySlotsBar.setSelectedSlot(selectedSlotId)
            self.__toysList.open(selectedSlotId)

    def __setSlotHighlight(self, slotId, isEnabled):
        if self.__hangarSpace.space is None:
            return
        else:
            customizationManager = CGF.getManager(self.__hangarSpace.spaceID, LobbyCustomizableObjectsManager)
            if customizationManager:
                customizationManager.updateSlotHighlight(slotId, isEnabled)
            return

    def __onDataUpdated(self, keys, _):
        if self.__SYNC_KEYS.issubset(set(keys)):
            with self.viewModel.transaction() as model:
                self.__updateSlots(fullUpdate=False, model=model)
                self.__updateSacks()

    def __onUpdateSlot(self, *args):
        with self.viewModel.transaction() as model:
            self.__updateSlots(fullUpdate=False, model=model)

    def __onTokensUpdate(self, tokens):
        if GuestsQuestsTokens.TOKEN_DOG in tokens:
            self.__updateMainState()

    def __onGoToGladeView(self):
        NewYearNavigation.switchTo(NYObjects.TOWN, True)

    def __clearBlur(self):
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        return

    def __onOpenBuySacksScreen(self):
        showBundlePurchaseDialog()
        if self._nyController.isSacksMarkerShown():
            self.__hideInfoMarker()

    def __hideInfoMarker(self):
        self._nyController.setIsSacksMarker(False)
        with self.viewModel.transaction() as model:
            model.setHasWidgetMarker(False)

    def __onOpenSack(self):
        self._nyController.sacksHelper.onOpenBox()

    def __onSackOpened(self, rewards):
        if rewards is None:
            return
        else:
            bonuses, _ = getLootboxBonuses(rewards)
            if not bonuses:
                return
            with self.viewModel.sacksModel.transaction() as model:
                model.setIsOpening(True)
                rewardsModel = model.getRewards()
                rewardsModel.clear()
                packBonusModelAndTooltipData(bonuses, rewardsModel, getNYSackRewardBonusPacker())
                rewardsModel.invalidate()
            return

    def __onOpenAnimationEnd(self):
        self.viewModel.sacksModel.setIsOpening(False)
        self.__updateSacks()

    def __hasDogToken(self):
        return self._nyController.isTokenReceived(GuestsQuestsTokens.TOKEN_DOG)
