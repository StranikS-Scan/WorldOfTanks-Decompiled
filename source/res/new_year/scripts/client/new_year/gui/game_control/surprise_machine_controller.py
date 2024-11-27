# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/surprise_machine_controller.py
from Event import Event, EventManager
from PlayerEvents import g_playerEvents
from helpers import dependency
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.ny_surprise_machine_model import MachineViews
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.robot_tv_screen_view_model import RobotTvScreenState
from new_year.gui.shared.ny_currency_provider import NyCurrencyProvider
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.ny_constants import MAX_LEVEL, SyncDataKeys
from new_year.skeletons.new_year import INewYearSurpriseMachine
from skeletons.gui.shared import IItemsCache
_CAN_APPLY_COIN_ROBOT_STATES = (RobotTvScreenState.IDLE, RobotTvScreenState.REWARDING, RobotTvScreenState.ERROR)
_CAN_APPLY_COIN_VIEW_STATES = (MachineViews.SPEND_TOKENS, MachineViews.SPEND_TOKENS_ACTIVE)

class NewYearSurpriseMachine(INewYearSurpriseMachine):
    __slots__ = ('__machineState', '__isMachineBusy', '__canApplyCoinState', '__isCanBuy', '__currencyProvider', '__machineViewState')
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__machineState = None
        self.__isMachineBusy = False
        self.__canApplyCoinState = None
        self.__isCanBuy = None
        self.__machineViewState = None
        self.__currencyProvider = NyCurrencyProvider()
        self.__em = EventManager()
        self.onMachineButtonPress = Event(self.__em)
        self.onStateUpdate = Event(self.__em)
        self.onUpdateApplyCoin = Event(self.__em)
        self.onMachineButtonHovered = Event(self.__em)
        return

    def onLobbyInited(self, _):
        self.__currencyProvider.initialize()
        g_playerEvents.onClientUpdated += self.__onDataUpdated
        if self.__isCanBuy is None:
            self.__isCanBuy = NewYearAtmospherePresenter.getLevel() == MAX_LEVEL
        self.__currencyProvider.onCurrencyUpdated += self.__onUpdateCurrency
        self.__updateApplyCoinState()
        return

    def onDisconnected(self):
        self.__currencyProvider.onCurrencyUpdated -= self.__onUpdateCurrency
        g_playerEvents.onClientUpdated -= self.__onDataUpdated
        self.__machineState = None
        self.__isMachineBusy = False
        self.__canApplyCoinState = None
        self.__isCanBuy = None
        self.__machineViewState = None
        self.__currencyProvider.finalize()
        return

    @property
    def canApplyCoin(self):
        return self.__canApplyCoinState

    @property
    def canBuyCoin(self):
        return self.__isCanBuy

    @property
    def machineState(self):
        return self.__machineState

    @property
    def isMachineBusy(self):
        return self.__isMachineBusy

    def setState(self, state):
        if self.__machineState != state:
            self.__machineState = state
            self.__updateApplyCoinState()
            self.onStateUpdate(self.__machineState)

    def setViewState(self, state):
        if self.__machineViewState != state:
            self.__machineViewState = state
            self.__updateApplyCoinState()

    def updateSurpriseMachineBusyStatus(self, isBusy):
        if self.__isMachineBusy != isBusy:
            self.__isMachineBusy = isBusy
            self.__updateApplyCoinState()

    def __updateApplyCoinState(self):
        canApplyCoin = self.__canApplyCoin()
        if self.__canApplyCoinState != canApplyCoin:
            self.__canApplyCoinState = canApplyCoin
            self.onUpdateApplyCoin()

    def __canApplyCoin(self):
        return self.__machineState in _CAN_APPLY_COIN_ROBOT_STATES and self.__machineViewState in _CAN_APPLY_COIN_VIEW_STATES and not self.__isMachineBusy and self.__currencyProvider.getCurrencyCount(NyCurrencyType.NYGIFTMACHINETOKEN) > 0

    def __onDataUpdated(self, diff, _):
        festivityKey = self._itemsCache.items.festivity.dataKey
        if SyncDataKeys.POINTS in diff.get(festivityKey, {}).keys():
            self.__isCanBuy = NewYearAtmospherePresenter.getLevel() == MAX_LEVEL

    def __onUpdateCurrency(self, cyrrency, diff):
        if cyrrency == NyCurrencyType.NYGIFTMACHINETOKEN:
            self.__updateApplyCoinState()
