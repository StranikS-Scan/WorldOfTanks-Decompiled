# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/gift_machine_controller.py
import logging
from Event import EventManager, Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_GIFT_MACHINE_BUY_TOKEN_VISITED
from constants import Configs
from gui import SystemMessages
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_machine.ny_gift_machine_view_model import MachineState
from gui.shared.notifications import NotificationPriorityLevel
from new_year.gift_machine_helper import getCoinID
from helpers import dependency, server_settings
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from new_year.ny_constants import SyncDataKeys, GuestsQuestsTokens
from new_year.ny_level_helper import NewYearAtmospherePresenter
from skeletons.gui.system_messages import ISystemMessages
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.new_year import IGiftMachineController, INewYearController, ICelebrityController
_CAN_APPLY_COIN_STATES = (MachineState.IDLE,
 MachineState.REWARD,
 MachineState.SPECIALREWARD,
 MachineState.RAREREWARD,
 MachineState.ERROR)
_CAN_SKIP_ANIM_STATES = (MachineState.REWARDPREQUEL, MachineState.SPECIALREWARDPREQUEL, MachineState.RAREREWARDPREQUEL)
_LOOTBOXES_TOOLTIP_CONFIG_NAME = Configs.LOOTBOXES_TOOLTIP_CONFIG.value
_logger = logging.getLogger(__name__)

class GiftMachineController(IGiftMachineController):
    __nyController = dependency.descriptor(INewYearController)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __celebrityController = dependency.descriptor(ICelebrityController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(GiftMachineController, self).__init__()
        self.__em = EventManager()
        self.onBuyStateChanged = Event(self.__em)
        self.onRedButtonStateChanged = Event(self.__em)
        self.onRedButtonPress = Event(self.__em)
        self.onSkipAnimStateChanged = Event(self.__em)
        self.onLootListInfoUpdated = Event(self.__em)
        self.onLootListInfoWindowStateChanged = Event(self.__em)
        self.onGoToBuyTokens = Event(self.__em)
        self.__canApplyCoinState = False
        self.__canSkipAnimState = False
        self.__canRedButtonPressState = False
        self.__isCanBuy = False
        self.__isMachineBusy = False
        self.__isMachineInRequest = False
        self.__state = None
        self.__lootListInfo = None
        return

    def fini(self):
        self.__em.clear()

    def onLobbyInited(self, event):
        self.__isCanBuy = self.__canBuy()
        self.__updateApplyCoinState()
        self.__nyController.onStateChanged += self.__updateState
        self.__nyController.currencies.onNyCoinsUpdate += self.__updateState
        self.__nyController.onDataUpdated += self.__onDataUpdated
        self.__celebrityController.onCelebCompletedTokensUpdated += self.__updateState
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged

    def onAvatarBecomePlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()

    @property
    def isBuyingCoinsAvailable(self):
        return self.__isCanBuy

    @property
    def isBuyCoinVisited(self):
        return True if not self.isBuyingCoinsAvailable else AccountSettings.getUIFlag(NY_GIFT_MACHINE_BUY_TOKEN_VISITED)

    @property
    def isEnable(self):
        return self.__nyController.isEnabled() and self.__nyController.currencies.getCoinsCount() > 0

    @property
    def isGiftMachineBusy(self):
        return self.__isMachineBusy

    @property
    def machineState(self):
        return self.__state

    @property
    def canApplyCoin(self):
        return self.__canApplyCoinState

    @property
    def canSkipAnim(self):
        return self.__canSkipAnimState

    @property
    def canRedButtonPress(self):
        return self.__canRedButtonPressState

    def getLootListInfo(self):
        if self.__lootListInfo is None:
            self.__updateLootListInfo()
        return self.__lootListInfo

    def updateGiftMachineBusyStatus(self, isBusy):
        if self.__isMachineBusy != isBusy:
            self.__isMachineBusy = isBusy
            self.__updateApplyCoinState()

    def setInRequestState(self, isInRequest):
        if self.__isMachineInRequest != isInRequest:
            self.__isMachineInRequest = isInRequest
            self.__updateApplyCoinState()

    def setMachineState(self, state):
        if self.__state != state:
            self.__state = state
            self.__updateApplyCoinState()

    def goToBuyState(self):
        self.onGoToBuyTokens()

    def __canApplyCoin(self):
        return self.isEnable and not self.__isMachineInRequest and not self.isGiftMachineBusy and self.machineState in _CAN_APPLY_COIN_STATES

    def __canSkipAnim(self):
        return self.__nyController.isEnabled() and not self.__isMachineInRequest and not self.isGiftMachineBusy and self.machineState in _CAN_SKIP_ANIM_STATES

    def __canRedButtonPress(self):
        return self.__canApplyCoinState or self.__canSkipAnimState

    def __clear(self):
        self.__nyController.onStateChanged -= self.__updateState
        self.__nyController.currencies.onNyCoinsUpdate -= self.__updateState
        self.__nyController.onDataUpdated -= self.__onDataUpdated
        self.__celebrityController.onCelebCompletedTokensUpdated -= self.__updateState
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged
        self.__canApplyCoinState = False
        self.__canSkipAnimState = False
        self.__canRedButtonPressState = False
        self.__isCanBuy = False
        self.__isMachineBusy = False
        self.__isMachineInRequest = False
        self.__state = None
        self.__lootListInfo = None
        return

    def __onDataUpdated(self, keys, _):
        if SyncDataKeys.LEVEL in keys:
            self.__updateState()

    def __updateState(self):
        isCanBuy = self.__canBuy()
        if self.__isCanBuy != isCanBuy:
            self.__isCanBuy = isCanBuy
            if isCanBuy:
                self.__showSysMessageMachineAvailable()
            self.onBuyStateChanged()
        self.__updateApplyCoinState()

    def __canBuy(self):
        return self.__nyController.isEnabled() and NewYearAtmospherePresenter.isMaxLevel() and self.__celebrityController.isGuestQuestsCompletedFully((GuestsQuestsTokens.GUEST_A,))

    def __updateApplyCoinState(self):
        canApplyCoin = self.__canApplyCoin()
        if self.__canApplyCoinState != canApplyCoin:
            self.__canApplyCoinState = canApplyCoin
        canSkipAnim = self.__canSkipAnim()
        if self.__canSkipAnimState != canSkipAnim:
            self.__canSkipAnimState = canSkipAnim
            self.onSkipAnimStateChanged()
        self.__updateRedButtonState()

    def __updateRedButtonState(self):
        canRedButtonPress = self.__canRedButtonPress()
        if self.__canRedButtonPressState != canRedButtonPress:
            self.__canRedButtonPressState = canRedButtonPress
            self.onRedButtonStateChanged()

    def __showSysMessageMachineAvailable(self):
        msgType = SystemMessages.SM_TYPE.NewYearGiftMachineAvailable
        priority = NotificationPriorityLevel.LOW
        auxData = [msgType,
         priority,
         None,
         None]
        serviceChannel = self.__systemMessages.proto.serviceChannel
        serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.NY_EVENT_BUTTON_MESSAGE, auxData=auxData)
        return

    def __updateLootListInfo(self, settingsDiff=None):
        config = settingsDiff.get(_LOOTBOXES_TOOLTIP_CONFIG_NAME, {}) if settingsDiff else self.__lobbyContext.getServerSettings().lootBoxesTooltipConfig.boxes
        self.__lootListInfo = config.get(getCoinID(), {})
        if not self.__lootListInfo:
            _logger.warning(_LOOTBOXES_TOOLTIP_CONFIG_NAME + " don't have needed box")

    @server_settings.serverSettingsChangeListener(_LOOTBOXES_TOOLTIP_CONFIG_NAME)
    def __onSettingsChanged(self, diff):
        self.__updateLootListInfo(diff)
        self.onLootListInfoUpdated()
