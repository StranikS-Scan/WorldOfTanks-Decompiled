# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/friend_glade/ny_friend_glade_view.py
import typing
from adisp import adisp_process
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.friend_glade.ny_resources_view_model import State
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.group_slots_model import GroupSlotsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.slot_model import SlotModel
from gui.impl.lobby.new_year.friends.resource_box_presenter import ResourceBoxPresenter
from gui.impl.lobby.new_year.ny_selectable_logic_presenter import SelectableLogicPresenter
from gui.impl.lobby.new_year.scene_rotatable_view import SceneRotatableView
from gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from gui.impl.lobby.new_year.tooltips.ny_resource_box_tooltip import NyResourceBoxTooltip
from gui.impl.new_year.navigation import ViewAliases, NewYearNavigation
from gui.impl.new_year.new_year_helper import nyCreateToolTipContentDecorator
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import NyResourcesEvent
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from helpers.time_utils import ONE_SECOND
from items.components.ny_constants import TOY_TYPES_BY_FRIEND_OBJECT, INVALID_TOY_ID
from ny_common.GeneralConfig import GeneralConfig
from new_year.friend_service_controller import BestFriendsDataKeys, FriendsDataKeys
from new_year.ny_constants import NyWidgetTopMenu, FRIEND_GLADE_TAB_TO_OBJECTS, CAMERA_OBJ_TO_FRIEND_GLADE_TAB
from new_year.ny_helper import getNYGeneralConfig
from new_year.ny_resource_collecting_helper import getAvgResourcesByCollecting
from skeletons.new_year import IFriendServiceController
if typing.TYPE_CHECKING:
    from gui.shared.event_dispatcher import NYTabCtx
    from gui.impl.gen.view_models.views.lobby.new_year.views.friend_glade.ny_friend_glade_view_model import NyFriendGladeViewModel
    from gui.impl.gen.view_models.views.lobby.new_year.views.friend_glade.ny_resources_view_model import NyResourcesViewModel

class NyFriendGladeView(SceneRotatableView, SelectableLogicPresenter):
    __slots__ = ('__currentObject', '__resourceBoxPresenter', '__showGreetings', '__delayer', '__isCollectRequestPending')
    _navigationAlias = ViewAliases.FRIEND_GLADE_VIEW
    __friendsService = dependency.descriptor(IFriendServiceController)

    def __init__(self, friendGladeModel, parentView):
        super(NyFriendGladeView, self).__init__(friendGladeModel, parentView)
        self.__currentObject = None
        self.__resourceBoxPresenter = None
        self.__showGreetings = False
        self.__delayer = CallbackDelayer()
        self.__isCollectRequestPending = False
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(NyFriendGladeView, self).initialize(*args, **kwargs)
        self.__showGreetings = kwargs.get('showGreetings', False)
        camObj = NewYearNavigation.getCurrentObject()
        newTab = CAMERA_OBJ_TO_FRIEND_GLADE_TAB.get(camObj)
        self.__currentObject = newTab
        self.__resourceBoxPresenter = ResourceBoxPresenter(self.viewModel.resourceBoxModel, self)
        self.__resourceBoxPresenter.initialize()
        with self.viewModel.transaction() as model:
            if self.__currentObject is not None:
                model.setTabName(self.__currentObject)
            self.__updateResourcesViewModel(model=model.resourcesViewModel)
            self.__updateWelcomeText(model=model)
            self.__updateSlots(fullUpdate=True, model=model)
        return

    def finalize(self):
        self.__delayer.clearCallbacks()
        self.__resourceBoxPresenter.finalize()
        self.__resourceBoxPresenter = None
        super(NyFriendGladeView, self).finalize()
        return

    @property
    def currentTab(self):
        return self.__currentObject

    def createToolTip(self, event):
        return self.__resourceBoxPresenter.createToolTip(event) or super(NyFriendGladeView, self).createToolTip(event)

    @nyCreateToolTipContentDecorator
    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.new_year.tooltips.NyResourceBoxTooltip():
            return NyResourceBoxTooltip(event.getArgument('isFriendsList'))
        if contentID == R.views.lobby.new_year.tooltips.NyDecorationTooltip():
            toyID = event.getArgument('toyID')
            return NyDecorationTooltip(toyID)
        return super(NyFriendGladeView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        events = super(NyFriendGladeView, self)._getEvents()
        return events + ((self.viewModel.resourcesViewModel.onCollect, self.__onCollect),
         (self.viewModel.resourcesViewModel.onSetFavoriteFriend, self.__onSetFavoriteFriend),
         (self.viewModel.resourcesViewModel.onGoToFriends, self.__onGoToFriendsView),
         (self.viewModel.resourcesViewModel.onHideFinishedStatus, self.__onHideFinishedStatus),
         (NewYearNavigation.onSidebarSelected, self.__onSideBarSelected),
         (NewYearNavigation.onUpdateCurrentView, self.__onUpdate),
         (self.__friendsService.onFriendHangarEnter, self.__onFriendHangarUpdate))

    def __onGoToFriendsView(self, *args, **kwargs):
        self._goToFriendsView(True, *args, **kwargs)

    def __onFriendHangarUpdate(self, *_):
        self.__updateAll()

    def __onUpdate(self, *_, **__):
        if self.getNavigationAlias() != NewYearNavigation.getCurrentViewName():
            return
        newObject = NewYearNavigation.getCurrentObject()
        newTab = CAMERA_OBJ_TO_FRIEND_GLADE_TAB.get(newObject)
        if self.__currentObject == newTab:
            return
        self.__currentObject = newTab
        self.__updateAll()
        NewYearNavigation.selectSidebarTabOutside(menuName=NyWidgetTopMenu.FRIEND_GLADE, tabName=newTab)

    def __updateSlots(self, fullUpdate, model):
        slotsData = self._nyController.requester.getSlotsData()
        groups = TOY_TYPES_BY_FRIEND_OBJECT.get(self.__currentObject, {})
        toys = self._nyController.requester.getToys()
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
                isEmpty = toyID == INVALID_TOY_ID
                if isEmpty:
                    icon = R.images.gui.maps.icons.newYear.decoration_types.craft_small.dyn(slotType)()
                else:
                    toy = toys[slotDescr.id][toyID]
                    icon = toy.getIcon()
                slot = SlotModel() if fullUpdate else groupModel.slots.getItem(slotIdx)
                slot.setSlotId(slotDescr.id)
                slot.setIsEmpty(isEmpty)
                slot.setToyId(toyID)
                slot.setIcon(icon)
                if fullUpdate:
                    groupModel.slots.addViewModel(slot)

        if fullUpdate:
            model.toySlotsBar.groupSlots.invalidate()

    def __onSideBarSelected(self, ctx):
        if ctx.menuName != NyWidgetTopMenu.FRIEND_GLADE:
            return
        tabName = ctx.tabName
        self.__currentObject = tabName
        camObj = FRIEND_GLADE_TAB_TO_OBJECTS.get(tabName)
        NewYearNavigation.switchTo(camObj, False)
        self.__updateAll()

    def __updateAll(self):
        with self.viewModel.transaction() as model:
            model.setTabName(self.__currentObject)
            self.__hideWelcomeText(model=model)
            self.__updateSlots(fullUpdate=True, model=model)
            self.__updateResourcesViewModel(model=model.resourcesViewModel)

    def __updateResourcesViewModel(self, model):
        bestFriends = self._friendsService.bestFriendList
        if self._friendsService.friendHangarSpaId not in bestFriends:
            if len(bestFriends) >= self._friendsService.maxBestFriendsCount:
                friendsCooldown = self.__friendsResourcesCollectCooldown(bestFriends)
                if friendsCooldown > 0.0:
                    model.setCooldown(friendsCooldown)
                    model.setState(State.LIMITTIMER)
                else:
                    model.setState(State.LIMIT)
            else:
                model.setState(State.NOTFAVORITE)
        else:
            cooldown = self._friendsService.getFriendCollectingCooldownTime()
            eventEndTimeTill = getNYGeneralConfig().getEventEndTime() - time_utils.getServerUTCTime()
            friendHangarSpaId = self._friendsService.friendHangarSpaId
            isFinishVisited = self._nyController.getFriendsResourcesFinishVisited(friendHangarSpaId)
            if cooldown > 0.0:
                if cooldown > eventEndTimeTill:
                    model.setState(State.FINISHEDHIDDEN if isFinishVisited else State.FINISHED)
                else:
                    model.setCooldown(self._friendsService.getFriendCollectingCooldownTime())
                    model.setState(State.TIMER)
                    self.__delayer.stopCallback(self.__cooldownUpdate)
                    self.__delayer.delayCallback(cooldown + ONE_SECOND, self.__cooldownUpdate)
            else:
                model.setState(State.AVAILABLE)
        model.setCollectAmount(getAvgResourcesByCollecting())

    def __friendsResourcesCollectCooldown(self, bestFriends):
        return min((max(bestFriendInfo[BestFriendsDataKeys.RESOURCES_COOLDOWN] - time_utils.getServerUTCTime(), 0) for bestFriendInfo in bestFriends.itervalues()))

    @adisp_process
    def __cooldownUpdate(self):
        isSuccess = yield self._friendsService.updateFriendList()
        if isSuccess:
            with self.viewModel.transaction() as model:
                self.__updateResourcesViewModel(model=model.resourcesViewModel)

    def __hideWelcomeText(self, model):
        self.__showGreetings = False
        model.setIsFirstVisit(False)

    def __updateWelcomeText(self, model):
        friendHangarState = self._friendsService.getFriendState()
        titleIdx, descriptionIdx = GeneralConfig.parseHangarNameMask(friendHangarState.get(FriendsDataKeys.HANGAR_NAME, 0))
        model.setIsFirstVisit(self.__showGreetings)
        model.hangarName.setTitle(titleIdx)
        model.hangarName.setDescription(descriptionIdx)
        model.setFriendName(self._friendsService.getFriendName(self._friendsService.friendHangarSpaId))

    @adisp_process
    def __onSetFavoriteFriend(self):
        isSuccess = yield self._friendsService.addBestFriend(self._friendsService.friendHangarSpaId)
        if isSuccess and self._friendsService.friendHangarSpaId in self._friendsService.bestFriendList:
            with self.viewModel.transaction() as model:
                self.__updateResourcesViewModel(model=model.resourcesViewModel)

    @adisp_process
    def __onCollect(self):
        if self.__isCollectRequestPending:
            return
        self.__isCollectRequestPending = True
        isSuccess = yield self._friendsService.collectFriendResources()
        self.__isCollectRequestPending = False
        if isSuccess:
            g_eventBus.handleEvent(NyResourcesEvent(eventType=NyResourcesEvent.FRIEND_RESOURCE_COLLECTED), scope=EVENT_BUS_SCOPE.LOBBY)
            with self.viewModel.transaction() as model:
                self.__updateResourcesViewModel(model=model.resourcesViewModel)

    def __onHideFinishedStatus(self):
        self._nyController.setFriendsResourcesFinishVisited(self._friendsService.friendHangarSpaId)
        self.viewModel.resourcesViewModel.setState(State.FINISHEDHIDDEN)
