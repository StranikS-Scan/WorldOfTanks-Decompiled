# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pet_system/event_view.py
import typing
import BigWorld
from frameworks.wulf import WindowFlags, WindowStatus
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.pet_system.event_view_model import EventViewModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.server_events.bonuses import getNonQuestBonuses, CreditsBonus, GoodiesBonus, ItemsBonus
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
from helpers import dependency
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from pet_system_common import pet_constants
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.pet_system import IPetSystemController
from skeletons.gui.system_messages import ISystemMessages
if typing.TYPE_CHECKING:
    from typing import List
    from gui.server_events.bonuses import SimpleBonus

class PetEvent(ViewComponent):
    LAYOUT_ID = R.aliases.common.none()
    __petController = dependency.descriptor(IPetSystemController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self, viewModel, ctx):
        super(PetEvent, self).__init__(layoutID=self.LAYOUT_ID, model=viewModel)
        self._ctx = ctx
        self.__packer = None
        self.__tooltipData = {}
        return

    def _onLoading(self, *args, **kwargs):
        super(PetEvent, self)._onLoading(*args, **kwargs)
        self.__packer = getDefaultBonusPacker()
        self._updateData()

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self._onServerSettingsChanged),)

    def createToolTip(self, event):
        if event.contentID == R.aliases.hangar.shared.PetEvent():
            tooltipData = self.getTooltipData(event)
            if not tooltipData:
                return None
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
            window.load()
            return window
        else:
            return super(PetEvent, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def _updateData(self):
        with self.getViewModel().transaction() as tx:
            eventID = self._ctx.get('eventID')
            eventType = self.__petController.getPetEventConfig().getEventType(eventID)
            tx.setEventId(eventID)
            tx.setEventType(eventType)
            self._updateRewards()

    def _updateRewards(self):
        rewardsData = self._ctx.get('rewards')
        if rewardsData:
            rewards = self.__getRewards(rewardsData[0])
            if not rewards:
                return
            with self.getViewModel().transaction() as tx:
                self.__tooltipData.clear()
                rewardsModel = tx.getRewards()
                rewardsModel.clear()
                packBonusModelAndTooltipData(rewards, rewardsModel, self.__tooltipData, self.__packer)
                rewardsModel.invalidate()
            self._pushRewardNotification(rewards)

    @staticmethod
    def __getRewards(rewardsData):
        rewards = []
        for key, value in rewardsData.iteritems():
            reward = getNonQuestBonuses(key, value)
            if reward:
                rewards.extend(reward)

        return rewards

    def _onServerSettingsChanged(self, diff):
        if pet_constants.PETS_SYSTEM_CONFIG in diff:
            if not self.__petController.isEnabled:
                self.destroyWindow()

    def _onClose(self):
        self.destroyWindow()

    def _pushRewardNotification(self, rewards):
        for item in rewards:
            if isinstance(item, CreditsBonus):
                self.__pushCreditsNotification(item)
            if isinstance(item, GoodiesBonus):
                self.__pushGoodieNotification(item)
            if isinstance(item, ItemsBonus):
                self.__pushItemNotification(item)

    def __pushCreditsNotification(self, item):
        data = {'amount': item.formatValue()}
        self.__systemMessages.proto.serviceChannel.pushClientMessage(data, SCH_CLIENT_MSG_TYPE.PET_SYSTEM_EVENT_CREDITS_AWARD)

    def __pushGoodieNotification(self, item):
        formattedList = item.formattedList()
        if formattedList:
            data = {'item': formattedList[0]}
            self.__systemMessages.proto.serviceChannel.pushClientMessage(data, SCH_CLIENT_MSG_TYPE.PET_SYSYEM_EVENT_ITEMS_AWARD)

    def __pushItemNotification(self, item):
        formattedItem = item.format()
        data = {'item': formattedItem}
        self.__systemMessages.proto.serviceChannel.pushClientMessage(data, SCH_CLIENT_MSG_TYPE.PET_SYSYEM_EVENT_ITEMS_AWARD)


class EventView(PetEvent):
    LAYOUT_ID = R.views.mono.pet_system.event_view()

    def __init__(self, ctx):
        super(EventView, self).__init__(EventViewModel, ctx)

    @property
    def viewModel(self):
        return super(EventView, self).getViewModel()

    def _getEvents(self):
        events = super(EventView, self)._getEvents()
        return events + ((self.viewModel.onClose, self._onClose),)


class EventViewWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(EventViewWindow, self).__init__(content=EventView(**kwargs), wndFlags=WindowFlags.WINDOW, layer=layer, areaID=R.areas.flattening_window())

    def show(self, focus=True):
        super(EventViewWindow, self).show(focus)
        self.center()

    def _onFocus(self, focused):
        if not focused and self.windowStatus not in (WindowStatus.DESTROYED, WindowStatus.DESTROYING):
            BigWorld.callback(0.5, self.destroy)
