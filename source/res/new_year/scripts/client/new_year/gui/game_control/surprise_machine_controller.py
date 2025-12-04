# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/surprise_machine_controller.py
from Event import Event, EventManager
from PlayerEvents import g_playerEvents
from helpers import dependency
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.ny_surprise_machine_model import MachineViews
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.robot_tv_screen_view_model import RobotTvScreenState
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.ny_constants import MAX_LEVEL, SyncDataKeys, NyBtnTypes
from new_year.skeletons.new_year import INewYearSurpriseMachine, INewYearCurrencyController
from skeletons.gui.shared import IItemsCache
_CAN_APPLY_COIN_ROBOT_STATES = (RobotTvScreenState.IDLE,
 RobotTvScreenState.REWARDING,
 RobotTvScreenState.ERROR,
 RobotTvScreenState.CHOOSEAMOUNT)
_CAN_APPLY_COIN_VIEW_STATES = (MachineViews.SPEND_TOKENS, MachineViews.SPEND_TOKENS_ACTIVE)

class NewYearSurpriseMachine(INewYearSurpriseMachine):
    __slots__ = ('__machineState', '__isMachineBusy', '__canApplyCoinState', '__isCanBuy', '__em', '__machineViewState', '__isActivated', '__selectedIdx', '__pendingApplyRefresh')
    _SELECTION_ORDER = (NyBtnTypes.LEFT, NyBtnTypes.RIGHT)
    _itemsCache = dependency.descriptor(IItemsCache)
    __nyCurrencyController = dependency.descriptor(INewYearCurrencyController)

    def __init__(self):
        self.__machineState = None
        self.__isMachineBusy = False
        self.__canApplyCoinState = None
        self.__isCanBuy = None
        self.__machineViewState = None
        self.__isActivated = False
        self.__pendingApplyRefresh = False
        self.__selectedIdx = 0
        self.__em = EventManager()
        self.onMachineButtonPress = Event(self.__em)
        self.onMachineSelectButtonPress = Event(self.__em)
        self.onStateUpdate = Event(self.__em)
        self.onUpdateApplyCoin = Event(self.__em)
        self.onMachineButtonHovered = Event(self.__em)
        self.onActivationChanged = Event(self.__em)
        self.onMachineBusyStatusUpdated = Event(self.__em)
        return

    def onLobbyInited(self, _):
        g_playerEvents.onClientUpdated += self.__onDataUpdated
        if self.__isCanBuy is None:
            self.__isCanBuy = NewYearAtmospherePresenter.getLevel() == MAX_LEVEL
        self.__nyCurrencyController.onCurrencyUpdated += self.__onUpdateCurrency
        self.__updateApplyCoinState()
        return

    def onDisconnected(self):
        self.__nyCurrencyController.onCurrencyUpdated -= self.__onUpdateCurrency
        g_playerEvents.onClientUpdated -= self.__onDataUpdated
        self.__machineState = None
        self.__isMachineBusy = False
        self.__canApplyCoinState = None
        self.__isCanBuy = None
        self.__machineViewState = None
        self.__isActivated = False
        self.__selectedIdx = 0
        return

    @property
    def isMachineActivated(self):
        return self.__isActivated

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

    @property
    def selectedBtnType(self):
        return self._SELECTION_ORDER[self.__selectedIdx]

    def moveSelectionLeft(self):
        self._moveSelection(-1)

    def moveSelectionRight(self):
        self._moveSelection(+1)

    def _moveSelection(self, delta):
        n = len(self._SELECTION_ORDER)
        self.__selectedIdx = (self.__selectedIdx + delta) % n

    def setState(self, state):
        if self.__machineState == state:
            return
        self.__machineState = state
        self.onStateUpdate(self.__machineState)

    def setViewState(self, state):
        if self.__machineViewState == state:
            return
        self.__machineViewState = state
        self.__updateApplyCoinState()

    def updateSurpriseMachineBusyStatus(self, isBusy):
        if self.__isMachineBusy == isBusy:
            return
        self.__isMachineBusy = isBusy
        if not isBusy and self.__pendingApplyRefresh:
            self.__pendingApplyRefresh = False
            self.__updateApplyCoinState()
        self.onMachineBusyStatusUpdated(isBusy)

    def tryActivateMachine(self):
        if self.__isActivated or not self.__canApplyCoin():
            return
        self.__resetSelection()
        self.__isActivated = True
        self.onActivationChanged(self.__isActivated)

    def deactivateMachine(self):
        if not self.__isActivated:
            return
        self.__resetSelection()
        self.__isActivated = False
        self.onActivationChanged(self.__isActivated)

    def handleSurpriseMachineBtnPress(self, btnType):
        if btnType == NyBtnTypes.PUSH:
            self.onMachineButtonPress()
        else:
            self.onMachineSelectButtonPress(btnType)

    def refreshApplyCoinState(self):
        self.__updateApplyCoinState()

    def __updateApplyCoinState(self):
        canApplyCoin = self.__canApplyCoin()
        if self.__isMachineBusy and self.__canApplyCoinState == canApplyCoin:
            return
        if self.__canApplyCoinState != canApplyCoin:
            self.__canApplyCoinState = canApplyCoin
            self.onUpdateApplyCoin()

    def __canApplyCoin(self):
        return self.__machineState in _CAN_APPLY_COIN_ROBOT_STATES and self.__machineViewState in _CAN_APPLY_COIN_VIEW_STATES and not self.__isMachineBusy and self.__nyCurrencyController.getGiftMachineTokenCount > 0

    def __onDataUpdated(self, diff, _):
        festivityKey = self._itemsCache.items.festivity.dataKey
        if SyncDataKeys.POINTS in diff.get(festivityKey, {}).keys():
            self.__isCanBuy = NewYearAtmospherePresenter.getLevel() == MAX_LEVEL

    def __onUpdateCurrency(self, currency, _):
        if currency == NyCurrencyType.NYGIFTMACHINETOKEN:
            if self.__isMachineBusy:
                self.__pendingApplyRefresh = True
                return
            self.__updateApplyCoinState()

    def __resetSelection(self):
        self.__selectedIdx = 0
