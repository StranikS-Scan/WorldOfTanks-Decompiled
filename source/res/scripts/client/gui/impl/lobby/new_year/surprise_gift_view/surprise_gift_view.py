# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/surprise_gift_view/surprise_gift_view.py
import BigWorld
from frameworks.wulf import ViewSettings, WindowLayer, WindowFlags
from gui.impl.gen.resources import R
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.gen.view_models.views.lobby.new_year.views.surprise_gift_view_model import SurpriseGiftViewModel
from gui.impl.pub import ViewImpl
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from gui.Scaleform.Waiting import Waiting
from chat_shared import SYS_MESSAGE_TYPE
from vehicle_systems.stricted_loading import makeCallbackWeak
from gui.server_events.event_items import Quest
from new_year.ny_helper import getNYGeneralConfig
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.lobby_context import ILobbyContext
from messenger.proto.events import g_messengerEvents
from ny_common.settings import NY_CONFIG_NAME, NYGeneralConsts
from debug_utils import LOG_DEBUG

class SurpriseGiftView(ViewImpl):
    __slots__ = ('__surpriseToken', '__isWaitingResponse')
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.SurpriseGiftView())
        settings.model = SurpriseGiftViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__surpriseToken = getNYGeneralConfig().getSurpriseToken()
        self.__isWaitingResponse = False
        super(SurpriseGiftView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SurpriseGiftView, self).getViewModel()

    def _getEvents(self):
        events = super(SurpriseGiftView, self)._getEvents()
        return events + ((self.viewModel.onClaim, self.__onClaim),
         (g_messengerEvents.serviceChannel.onChatMessageReceived, self.__onChatMessageReceived),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingChanged),
         (self.__eventsCache.onSyncCompleted, self.__onEventsCacheSyncCompleted),
         (self.viewModel.closeWindow, self.__closeWindow))

    def _onLoading(self, *args, **kwargs):
        self._update()
        NewYearSoundsManager.setOverlayState(True)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CELEBRITY_SCREEN_REWARD)
        super(SurpriseGiftView, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        self.__surpriseToken = None
        self.__isWaitingResponse = None
        NewYearSoundsManager.setOverlayState(False)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CELEBRITY_SCREEN_REWARD_EXIT)
        super(SurpriseGiftView, self)._finalize()
        return

    def _update(self):
        tokenQuest = self.__getSurpriseTokenQuest()
        if tokenQuest is None:
            LOG_DEBUG('TokenQuest is not exists', self.__surpriseToken)
            self.destroyWindow()
        else:
            with self.viewModel.transaction() as model:
                model.setDescription(tokenQuest.getDescription())
        return

    def __isSurpriseQuest(self, quest):
        questId = quest if isinstance(quest, str) else quest.getID()
        return questId.startswith(self.__surpriseToken)

    def __getSurpriseTokenQuest(self):
        quests = self.__eventsCache.getAllQuests(self.__isSurpriseQuest)
        return quests.get(self.__surpriseToken)

    def __onClaim(self):
        if self.__isWaitingResponse:
            return
        Waiting.show('synchronize')
        self.__requestToken()

    def __closeWindow(self):
        if self.__isWaitingResponse:
            return
        self.destroyWindow()

    def __requestToken(self):
        self.__isWaitingResponse = True
        BigWorld.player().requestSingleToken(self.__surpriseToken)

    def __onChatMessageReceived(self, *args):
        _, message = args
        tokenQuestRewards = None
        if message is not None and message.type == SYS_MESSAGE_TYPE.tokenQuests.index() and message.data is not None:
            tokenQuestRewards = message.data.get('detailedRewards', {}).get(self.__surpriseToken)
        if tokenQuestRewards is None:
            return
        else:
            Waiting.hide('synchronize')
            self.__isWaitingResponse = False
            vehicleCD = self.__getvehicleCD(tokenQuestRewards)
            if vehicleCD is not None:
                BigWorld.callback(1.0, makeCallbackWeak(g_currentVehicle.selectVehicleByCD, vehicleCD=vehicleCD))
            self.destroyWindow()
            return

    def __getvehicleCD(self, tokenQuestRewards):
        vehicleCD = None
        vehicleData = tokenQuestRewards.get('vehicles', [])
        if vehicleData:
            vehicleCD = vehicleData[0].keys()[0]
        return vehicleCD

    def __onServerSettingChanged(self, diff):
        if diff.get(NY_CONFIG_NAME, {}).get(NYGeneralConsts.CONFIG_NAME) is None:
            return
        else:
            newSurpriseToken = getNYGeneralConfig().getSurpriseToken()
            if self.__surpriseToken != newSurpriseToken:
                self.__surpriseToken = newSurpriseToken
                self.__updateAfterSync()
            return

    def __onEventsCacheSyncCompleted(self):
        self.__updateAfterSync()

    def __updateAfterSync(self):
        isTokenQuestExists = self.__getSurpriseTokenQuest() is not None
        if isTokenQuestExists:
            if self.__isWaitingResponse:
                self.__requestToken()
            self._update()
        else:
            LOG_DEBUG('TokenQuest is not exists, closing SurpriseGiftView', self.__surpriseToken)
            Waiting.hide('synchronize')
            self.destroyWindow()
        return


class SurpriseGiftWindow(LobbyWindow):

    def __init__(self):
        super(SurpriseGiftWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=SurpriseGiftView(), layer=WindowLayer.OVERLAY)
