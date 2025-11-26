# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/services/campaign_service.py
import logging
from typing import List
from account_helpers.settings_core.settings_constants import PersonalMission3
from shared_utils import first
from personal_missions import PM_BRANCH
from PlayerEvents import g_playerEvents
from helpers import dependency
from config_schemas.umg_config import umgConfigSchema
from gui.shared import g_eventBus, events
from gui.impl.lobby.user_missions.hangar_widget.services.events_service import _EntryPointData
from gui.impl.lobby.user_missions.hangar_widget.services import ICampaignService
from gui.impl.lobby.personal_missions_30.views_helpers import isOperationAvailableByVehicles, getSortedPm3Operations
from gui.impl.lobby.user_missions.hangar_widget.event_banners.pm3_event_banner import PM3EventBannerTeaser, PM3EventBannerOperation1, PM3EventBannerOperation2, PM3EventBannerOperation3
from gui.impl.lobby.personal_missions_30.personal_mission_constants import OperationIDs
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.impl.lobby.personal_missions_30.views_helpers import markBannerAnimationShown
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IHangarGuiController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
BANNER_TEASER_ID = 'teaser'
BANNER_OPERATION_ONE_ID = str(OperationIDs.OPERATION_FIRST.value)
BANNER_OPERATION_TWO_ID = str(OperationIDs.OPERATION_SECOND.value)
BANNER_OPERATION_THREE_ID = str(OperationIDs.OPERATION_THIRD.value)

class CampaignService(ICampaignService):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)
    pm3bannerMap = {BANNER_TEASER_ID: PM3EventBannerTeaser.NAME,
     BANNER_OPERATION_ONE_ID: PM3EventBannerOperation1.NAME,
     BANNER_OPERATION_TWO_ID: PM3EventBannerOperation2.NAME,
     BANNER_OPERATION_THREE_ID: PM3EventBannerOperation3.NAME}

    def __init__(self):
        super(CampaignService, self).__init__()
        self.__visibleEntry = None
        EventBannersContainer().registerEventBanner(PM3EventBannerTeaser)
        EventBannersContainer().registerEventBanner(PM3EventBannerOperation1)
        EventBannersContainer().registerEventBanner(PM3EventBannerOperation2)
        EventBannersContainer().registerEventBanner(PM3EventBannerOperation3)
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
        return

    def getEntries(self):
        return [self.__visibleEntry] if self.__visibleEntry is not None else []

    def onPrbEntitySwitched(self):
        self.__tryToUpdateBanner()

    def startListening(self):
        g_playerEvents.onConfigModelUpdated += self._needToUpdateBanner
        self.__itemsCache.onSyncCompleted += self._needToUpdateBanner
        self.__eventsCache.onPMSyncCompleted += self._needToUpdateBanner
        self.__lobbyContext.onServerSettingsChanged += self._needToUpdateBanner
        self.startGlobalListening()
        self.__tryToUpdateBanner()

    def stopListening(self):
        self.__tryToUpdateVisibleEntry(None)
        self.stopGlobalListening()
        self.__lobbyContext.onServerSettingsChanged -= self._needToUpdateBanner
        self.__eventsCache.onPMSyncCompleted -= self._needToUpdateBanner
        self.__itemsCache.onSyncCompleted -= self._needToUpdateBanner
        g_playerEvents.onConfigModelUpdated -= self._needToUpdateBanner
        return

    def finalize(self):
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        g_playerEvents.onAccountBecomeNonPlayer -= self.__onAccountBecomeNonPlayer
        self.stopListening()

    def _needToUpdateBanner(self, *_, **__):
        self.__tryToUpdateBanner()

    def __tryToUpdateBanner(self):
        if self.__isBannerVisible():
            currentOperation = first(self.__getActiveOperationsForPM3())
            pm3BannerOperationID = str(currentOperation.getID()) if currentOperation is not None else BANNER_TEASER_ID
            pm3BannerData = {'id': self.pm3bannerMap.get(pm3BannerOperationID),
             'startDate': '01.01.2020 00:00',
             'endDate': '24.09.2025 23:59',
             'weightConfig': 'PM3EntryPoint'}
            entry = _EntryPointData(pm3BannerData)
            if entry.isValidData():
                self.__tryToUpdateVisibleEntry(None if entry.isExpiredDate() else entry)
        else:
            self.__tryToUpdateVisibleEntry(None)
            markBannerAnimationShown(PersonalMission3.PM_BANNER_ANIMATION_KEY, reset=True)
        return

    def __isBannerVisible(self):
        isPM3BannerEnabled = umgConfigSchema.getModel().enablePM3Banner
        if not isPM3BannerEnabled:
            return False
        else:
            serverSettings = self.__lobbyContext.getServerSettings()
            if not serverSettings.isPersonalMissionsEnabled(PM_BRANCH.PERSONAL_MISSION_3):
                return False
            if not self.__hangarGuiCtrl.currentGuiProvider.getMissionsHelper().isPM3MissionsSupported():
                return False
            operationsPM3 = getSortedPm3Operations()
            pm3ActiveOperations = self.__getActiveOperationsForPM3()
            currentOperation = first(pm3ActiveOperations)
            currentOperation = currentOperation if currentOperation is not None else first(operationsPM3.values())
            isPM3Available = isOperationAvailableByVehicles(currentOperation)
            isAnyPM3Active = len(pm3ActiveOperations) > 0
            isPM3FullyCompleted = all((operation.isFullCompleted() for operation in operationsPM3.values()))
            return not isPM3FullyCompleted and (isPM3Available or isAnyPM3Active) and not currentOperation.isDisabled()

    def __getActiveOperationsForPM3(self):
        return self.__eventsCache.getPersonalMissions().getActiveOperations(PM_BRANCH.V2_BRANCHES)

    def __tryToUpdateVisibleEntry(self, entry):
        if self.__visibleEntry != entry:
            self.__visibleEntry = entry
            self.onEventsListChanged()

    def __onLobbyInited(self, *_):
        self.startListening()

    def __onAccountBecomeNonPlayer(self):
        self.stopListening()
