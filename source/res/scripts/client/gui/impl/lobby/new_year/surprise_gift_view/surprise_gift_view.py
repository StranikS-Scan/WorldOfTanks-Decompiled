# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/surprise_gift_view/surprise_gift_view.py
import BigWorld
from frameworks.wulf import ViewSettings, WindowLayer, WindowFlags
from gui.Scaleform.daapi.view.lobby.customization.shared import isC11nEnabled, CustomizationTabs
from gui.impl.gen.resources import R
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.gen.view_models.views.lobby.new_year.views.surprise_gift_view_model import SurpriseGiftViewModel
from gui.impl.pub import ViewImpl
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from vehicle_systems.stricted_loading import makeCallbackWeak
from gui.server_events.event_items import Quest
from new_year.ny_helper import getNYGeneralConfig
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from debug_utils import LOG_DEBUG

class SurpriseGiftView(ViewImpl):
    __slots__ = ('__surpriseToken',)
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)
    __customizationService = dependency.descriptor(ICustomizationService)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.SurpriseGiftView())
        settings.model = SurpriseGiftViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__surpriseToken = getNYGeneralConfig().getSurpriseToken()
        super(SurpriseGiftView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SurpriseGiftView, self).getViewModel()

    def _getEvents(self):
        events = super(SurpriseGiftView, self)._getEvents()
        return events + ((self.viewModel.onGoToHangar, self.__closeWindow), (self.viewModel.onGoToAttachments, self.__goToAttachments), (self.__nyController.onStateChanged, self.__onEventStateChanged))

    def _onLoading(self, *args, **kwargs):
        self._update()
        NewYearSoundsManager.setOverlayState(True)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CELEBRITY_SCREEN_REWARD)
        super(SurpriseGiftView, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        self.__surpriseToken = None
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
            vehicleCD = self.__getVehicleCD(self.__getSurpriseTokenQuest())
            with self.viewModel.transaction() as model:
                model.setDescription(tokenQuest.getDescription())
                model.setVehicleName(self.__getVehicleName(vehicleCD))
        return

    def __isSurpriseQuest(self, quest):
        questId = quest if isinstance(quest, str) else quest.getID()
        return questId.startswith(self.__surpriseToken)

    def __getSurpriseTokenQuest(self):
        quests = self.__eventsCache.getAllQuests(self.__isSurpriseQuest)
        return quests.get(self.__surpriseToken)

    def __closeWindow(self):
        vehicleCD = self.__getVehicleCD(self.__getSurpriseTokenQuest())
        if vehicleCD is not None:
            BigWorld.callback(1.0, makeCallbackWeak(g_currentVehicle.selectVehicleByCD, vehicleCD=vehicleCD))
        self.destroyWindow()
        return

    @staticmethod
    def __getVehicleCD(tokenQuestRewards):
        vehicleCD = None
        vehicleData = tokenQuestRewards.getBonuses('vehicles', [])
        if vehicleData:
            vehicleCD = vehicleData[0].getValue().keys()[0]
        return vehicleCD

    def __getVehicleName(self, vehicleCD):
        return self.__itemsCache.items.getItemByCD(vehicleCD).userName

    def __onEventStateChanged(self):
        if not self.__nyController.isEnabled():
            self.destroyWindow()

    def __goToAttachments(self):
        if isC11nEnabled():
            vehicleCD = self.__getVehicleCD(self.__getSurpriseTokenQuest())
            hangarVehId = self.__itemsCache.items.getItemByCD(vehicleCD).invID
            self.__customizationService.showCustomization(vehInvID=hangarVehId, tabId=CustomizationTabs.ATTACHMENTS)
        self.destroyWindow()


class SurpriseGiftWindow(LobbyWindow):

    def __init__(self):
        super(SurpriseGiftWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=SurpriseGiftView(), layer=WindowLayer.OVERLAY)
