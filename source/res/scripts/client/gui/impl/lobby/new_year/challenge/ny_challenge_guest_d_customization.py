# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_guest_d_customization.py
import CGF
import typing
from frameworks.wulf import ViewSettings, ViewModel
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_DOG_INFO_VISITED, NY_DOG_PAGE_VISITED
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.group_slots_model import GroupSlotsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.slot_model import SlotModel
from gui.impl.lobby.new_year.glade.ny_toys_list import NyToysList
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from gui.impl.lobby.new_year.tooltips.ny_decoration_unavailable_tooltip import NyDecorationUnavailableTooltip
from gui.impl.pub import ViewImpl
from gui.impl.lobby.new_year.tooltips.ny_purchased_decoration_tooltip import NyPurchasedDecorationTooltip
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from helpers import dependency, uniprof
from items.components.ny_constants import GUEST_D_SLOT_GROUPS, INVALID_TOY_ID
from new_year.newyear_cgf_components.lobby_customization_components import LobbyCustomizableObjectsManager
from new_year.ny_constants import SyncDataKeys
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_model import NewYearChallengeModel
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_guest_d_customization_model import NewYearGuestDCustomizationModel

class NyChallengeGuestDCustomization(NyHistoryPresenter):
    __slots__ = ('__toysList',)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __SYNC_KEYS = {SyncDataKeys.INVENTORY_TOYS, SyncDataKeys.SLOTS}

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(NyChallengeGuestDCustomization, self).__init__(viewModel, parentView, soundConfig)
        self.__toysList = NyToysList()

    @property
    def viewModel(self):
        model = self.getViewModel()
        return model.guestDCustomizationModel

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyDogTooltip():
            return ViewImpl(ViewSettings(R.views.lobby.new_year.tooltips.NyDogTooltip(), model=ViewModel()))
        if contentID == R.views.lobby.new_year.tooltips.NyDecorationTooltip():
            toyID = event.getArgument('toyID')
            return NyDecorationTooltip(toyID)
        if contentID == R.views.lobby.new_year.tooltips.NyDecorationUnavailableTooltip():
            toyID = event.getArgument('toyID')
            return NyDecorationUnavailableTooltip(toyID)
        if contentID == R.views.lobby.new_year.tooltips.NyPurchasedDecorationTooltip():
            toyID = event.getArgument('toyID')
            state = event.getArgument('state')
            return NyPurchasedDecorationTooltip(toyID, state)
        return super(NyChallengeGuestDCustomization, self).createToolTipContent(event, contentID)

    @uniprof.regionDecorator(label='ny_challenge_guest_d_customization', scope='enter')
    def initialize(self, *args, **kwargs):
        super(NyChallengeGuestDCustomization, self).initialize(*args, **kwargs)
        self.__toysList.initialize(self.viewModel.toySlotsBar)
        with self.viewModel.transaction() as model:
            self.__updateSlots(fullUpdate=True, model=model)
            self.__updateTutorial()
        if not AccountSettings.getUIFlag(NY_DOG_PAGE_VISITED):
            AccountSettings.setUIFlag(NY_DOG_PAGE_VISITED, True)
            g_eventBus.handleEvent(events.NyDogEvent(events.NyDogEvent.DOG_PAGE_VISITED), scope=EVENT_BUS_SCOPE.LOBBY)

    @uniprof.regionDecorator(label='ny_challenge_guest_d_customization', scope='exit')
    def finalize(self):
        super(NyChallengeGuestDCustomization, self).finalize()
        self.__toysList.finalize()

    def _getEvents(self):
        return super(NyChallengeGuestDCustomization, self)._getEvents() + ((self.viewModel.toySlotsBar.onHoverSlot, self.__onHoverSlot),
         (self.viewModel.toySlotsBar.onHoverOutSlot, self.__onHoverOutSlot),
         (self.viewModel.toySlotsBar.onSelectSlot, self.__onSelectSlot),
         (self._nyController.onDataUpdated, self.__onDataUpdated))

    def _getListeners(self):
        return ((events.NyDogEvent.HOVER_IN, self.__onHoverInDog, EVENT_BUS_SCOPE.DEFAULT), (events.NyDogEvent.HOVER_OUT, self.__onHoverOutDog, EVENT_BUS_SCOPE.DEFAULT))

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
                if fullUpdate:
                    groupModel.slots.addViewModel(slot)

        if fullUpdate:
            model.toySlotsBar.groupSlots.invalidate()

    def __updateTutorial(self):
        self.viewModel.setHasTutorial(not AccountSettings.getUIFlag(NY_DOG_INFO_VISITED))

    def __onHoverInDog(self, _):
        self.viewModel.setShowDogTooltip(True)

    def __onHoverOutDog(self, _):
        self.viewModel.setShowDogTooltip(False)

    def __onHoverSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), True)

    def __onHoverOutSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), False)

    def __onSelectSlot(self, args):
        if not AccountSettings.getUIFlag(NY_DOG_INFO_VISITED):
            AccountSettings.setUIFlag(NY_DOG_INFO_VISITED, True)
        with self.viewModel.transaction() as model:
            selectedSlotId = int(args['slotId'])
            model.toySlotsBar.setSelectedSlot(selectedSlotId)
            self.__toysList.open(selectedSlotId)
        self.__updateTutorial()

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
