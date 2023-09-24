# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback_call/winback_call_main_view.py
import logging
import typing
import BigWorld
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.backport import BackportContextMenuWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_main import WinbackCallFriendMain
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_records import WinbackCallFriendRecords
from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_main_view_model import WinbackCallMainViewModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.winback_call.backports import getWinBackCallFrindContextMenuData
from gui.impl.lobby.winback_call.winback_call_helper import getWinBackBonusPacker, getWinBackCallBonuses, getWinBackCallQuest, fillFriendBaseData
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared import utils, event_dispatcher
from gui.shared.event_dispatcher import openWinBackCallErrorView
from gui.shared.event_dispatcher import showHangar
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
from gui.shared.utils import decorators
from gui.sounds.filters import switchHangarFilteredFilter
from helpers import dependency
from items import vehicles
from skeletons.gui.game_control import IWinBackCallController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from uilogging.winback_call.constants import WinbackCallLogItem, WinbackCallLogScreenParent
from uilogging.winback_call.loggers import WinBackCallLogger
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.impl.gen.view_models.views.lobby.winback_call.winback_call_friend_vehicle import WinbackCallFriendVehicle
    from gui.game_control.winback_call_controller import _FriendsCache, _WinbackCallWebResponse
_logger = logging.getLogger(__name__)

class WinbackCallMainView(ViewImpl):
    __winBackCallCtrl = dependency.descriptor(IWinBackCallController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.winback_call.WinbackCallMainView())
        settings.model = WinbackCallMainViewModel()
        super(WinbackCallMainView, self).__init__(settings)
        self.__copiedLink = None
        self.__bonusPacker = None
        self.__friendsStorage = None
        self.__tooltips = {}
        self.__wbcLogger = WinBackCallLogger()
        return

    def _initialize(self, *args, **kwargs):
        super(WinbackCallMainView, self)._initialize(*args, **kwargs)
        switchHangarFilteredFilter(on=True)

    def _finalize(self):
        switchHangarFilteredFilter(on=False)
        self.__clearFriendsStorage()
        self.__bonusPacker = None
        super(WinbackCallMainView, self)._finalize()
        return

    @property
    def viewModel(self):
        return super(WinbackCallMainView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(WinbackCallMainView, self).createToolTip(event)

    def getTooltipData(self, event):
        if not self.isFocused:
            return
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        elif tooltipId in self.__tooltips:
            return self.__tooltips[tooltipId]
        elif tooltipId == WinbackCallMainViewModel.FRIEND_VEHICLE_TOOLTIP_ID:
            vehicleCD = event.getArgument('vehicleCD')
            if vehicleCD is None:
                return
            return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.SHOP_VEHICLE, specialArgs=(vehicleCD,))
        else:
            return

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            contextMenuData = getWinBackCallFrindContextMenuData(event)
            if contextMenuData is not None:
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.load()
                return window
        return super(WinbackCallMainView, self).createContextMenu(event)

    def _getEvents(self):
        events = super(WinbackCallMainView, self)._getEvents()
        return events + ((self.__winBackCallCtrl.onConfigChanged, self.__onConfigChanged),
         (self.__winBackCallCtrl.onFriendStatusUpdated, self.__onFriendStatusUpdated),
         (self.__winBackCallCtrl.onStateChanged, self.__onStateChanged),
         (self.__winBackCallCtrl.onFriendsUpdated, self.__onFriendsUpdated),
         (self.__eventsCache.onSyncCompleted, self.__onSyncCompleted),
         (self.viewModel.onCopyLink, self.__onCopyLink),
         (self.viewModel.onOpenSubmissionForm, self.__onOpenSubmissionForm))

    def _onLoaded(self, *args, **kwargs):
        super(WinbackCallMainView, self)._onLoaded(*args, **kwargs)
        self.__update()
        self.__requestFriendList()

    def __onConfigChanged(self):
        with self.viewModel.transaction() as model:
            self.__updateStaticData(model)

    def __onSyncCompleted(self, *_):
        with self.viewModel.transaction() as model:
            self.__updateRewards(model)

    def __onFriendStatusUpdated(self):
        if self.__friendsStorage:
            self.__updateFriends(self.__friendsStorage)

    def __onFriendsUpdated(self, friendsData):
        self.__updateFriends(friendsData)

    def __onStateChanged(self):
        if self.__winBackCallCtrl.isEnabled:
            self.__update()
        else:
            showHangar()
            self.destroyWindow()

    def __update(self):
        with self.viewModel.transaction() as model:
            self.__updateStaticData(model)
            self.__updateRewards(model)

    def __updateStaticData(self, model):
        startTime, endTime = self.__winBackCallCtrl.eventPeriod()
        model.setEventStart(startTime)
        model.setEventFinish(endTime)

    def __onCopyLink(self):
        self.__wbcLogger.handleClick(WinbackCallLogItem.LINK_BUTTON, WinbackCallLogScreenParent.MAIN_VIEW)
        self.viewModel.setIsLinkCopied(bool(self.__copiedLink))
        if self.__copiedLink:
            utils.copyToClipboard(self.__copiedLink)

    def __onOpenSubmissionForm(self):
        self.__wbcLogger.handleClick(WinbackCallLogItem.FRIENDS_FORM_BUTTON, WinbackCallLogScreenParent.MAIN_VIEW)
        if self.__friendsStorage is not None and self.__friendsStorage.friends:
            event_dispatcher.openWinBackCallFriendListView(self.__friendsStorage, parent=self.getParentWindow())
        return

    def __updateRewards(self, model):
        winBackQuest = getWinBackCallQuest()
        if winBackQuest is None:
            return
        else:
            bonuses = getWinBackCallBonuses()
            rewardsModel = model.getRewards()
            rewardsModel.clear()
            packBonusModelAndTooltipData(bonuses, rewardsModel, self.__tooltips, packer=self.__getBonusPacker())
            model.setIsRewardsReceived(winBackQuest.isCompleted())
            return

    @decorators.adisp_process('updatingFriendList', softStart=True)
    def __requestFriendList(self):
        response = yield self.__winBackCallCtrl.getFriendsList()
        if response.isSuccess:
            self.__updateFriends(response.data)
        else:
            BigWorld.callback(0.1, self.__showError)

    def __showError(self):
        openWinBackCallErrorView(self.getParentWindow())

    def __getBonusPacker(self):
        if self.__bonusPacker is None:
            self.__bonusPacker = getWinBackBonusPacker()
        return self.__bonusPacker

    def __updateFriends(self, friendsData):
        self.__friendsStorage = friendsData
        self.__copiedLink = friendsData.inviteUrl
        with self.viewModel.transaction() as model:
            friendsModel = model.getFriends()
            friendsModel.clear()
            returnedCount = 0
            for friend in friendsData.friends:
                friendModel = WinbackCallFriendMain()
                fillFriendBaseData(friendModel, friend)
                self.__fillRecords(friendModel.getRecords(), friend.serviceRecords)
                self.__fillVehicle(friendModel.vehicle, friend.vehicleName)
                friendsModel.addViewModel(friendModel)
                if friend.isRolledBack:
                    returnedCount += 1

            model.setFriendsBack(returnedCount)
            model.setCanSendInvite(friendsData.canSendInvite)
            friendsModel.invalidate()

    def __fillRecords(self, model, serviceRecords):
        model.clear()
        for record in serviceRecords.getRecords():
            recordModel = WinbackCallFriendRecords()
            recordModel.setType(record.name)
            recordModel.setValue(record.value)
            model.addViewModel(recordModel)

        model.invalidate()

    def __fillVehicle(self, vehicleModel, vehTypeName):
        vehDescr = vehicles.VehicleDescr(typeName=vehTypeName)
        vehicleIntCD = vehDescr.type.compactDescr
        vehicle = self.__itemsCache.items.getItemByCD(vehicleIntCD)
        vehicleModel.setIntCD(vehicle.intCD)
        vehicleModel.setName(vehicle.userName)
        vehicleModel.setIcon(getIconResourceName(getNationLessName(vehicle.name)))
        vehicleModel.setIsElite(vehicle.isElite)
        vehicleModel.setType(vehicle.type)
        vehicleModel.setLevel(vehicle.level)
        vehicleModel.setNation(vehicle.nationName)

    def __clearFriendsStorage(self):
        if self.__friendsStorage is not None:
            self.__friendsStorage.clear()
            self.__friendsStorage = None
        return


class WinbackCallMainViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WinbackCallMainViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WinbackCallMainView(), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)
