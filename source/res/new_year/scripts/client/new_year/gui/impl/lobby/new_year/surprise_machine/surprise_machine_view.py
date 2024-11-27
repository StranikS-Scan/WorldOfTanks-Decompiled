# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/surprise_machine/surprise_machine_view.py
import copy
from functools import partial
import WWISE
import typing
from adisp import adisp_process
from frameworks.wulf import WindowLayer, WindowFlags
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.pub import WindowImpl
from gui.impl.gen import R
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import selectVehicleInHangar
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from helpers import time_utils
from helpers.func_utils import waitEventAndCall
from lootboxes_common import makeLootboxID
from messenger.formatters.service_channel import QuestAchievesFormatter
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.ny_surprise_machine_model import PurchaseFormState, MachineViews
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.robot_tv_screen_view_model import RobotTvScreenState
from new_year.gui.impl.new_year.sounds import NewYearSoundEvents, NewYearSoundsManager, NewYearSoundStates, NewYearSoundVars
from new_year.gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from new_year.gui.impl.lobby.new_year.surprise_machine.robot_tv_screen_view import RobotTvScreenView
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.gui.shared.gui_items.processors.ny_processor import BuyMachineCoinsProcessor
from new_year.gui.shared.ny_machine_helper import getMachineLootboxToken
from new_year.helpers.server_settings import getNewYearMachineConfig
from new_year.ny_constants import InternalViewState, ViewAliases
from new_year.skeletons.new_year import INewYearSurpriseMachine, INewYearController
from shared_utils import first
from skeletons.gui.impl import INewYearNavigation
from skeletons.gui.shared import IItemsCache
from wg_async import AsyncScope, AsyncEvent
if typing.TYPE_CHECKING:
    from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.ny_surprise_machine_model import NySurpriseMachineModel
_TEXTURE_PATH = 'content/Hangars/h03_mt_ny_2025/environment/hd_h03_NY25_0015_Robot_1_AM.dds'

def isRewardVehicle(reward):
    return reward and 'vehicles' in reward


_INTERNAL_STATE_TO_MACHINE_VIEW = {InternalViewState.MACHINE_MAIN: MachineViews.SPEND_TOKENS,
 InternalViewState.BUY_MACHINE_COIN: MachineViews.GET_TOKENS,
 InternalViewState.MACHINE_REWARDING: MachineViews.SPEND_TOKENS_ACTIVE,
 InternalViewState.VEHICLE_MACHINE_REWARDING: MachineViews.SPEND_TOKENS_ACTIVE}

class NySurpriseMachineView(HistorySubModelPresenter):
    __slots__ = ('__displayView', '__asyncScope', '__finishRewardEvent', '__machineConfig', '__goToRewardVehicleEvent', '__onCoinAppliedEvent', '__state')
    _INTERNAL_VIEW_STATE = InternalViewState.MACHINE_MAIN
    __itemsCache = dependency.descriptor(IItemsCache)
    __newYearNavigation = dependency.descriptor(INewYearNavigation)
    __nyMachineController = dependency.descriptor(INewYearSurpriseMachine)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, model, parentView):
        super(NySurpriseMachineView, self).__init__(model, parentView)
        self.__displayView = None
        self.__machineConfig = getNewYearMachineConfig()
        self.__asyncScope = None
        self.__finishRewardEvent = None
        self.__onCoinAppliedEvent = None
        self.__goToRewardVehicleEvent = None
        self.__state = True
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(NySurpriseMachineView, self).initialize(*args, **kwargs)
        self.__asyncScope = AsyncScope()
        self.__finishRewardEvent = AsyncEvent(scope=self.__asyncScope)
        self.__onCoinAppliedEvent = AsyncEvent(scope=self.__asyncScope)
        self.__goToRewardVehicleEvent = AsyncEvent(scope=self.__asyncScope)
        self.__displayView.viewModel.rewardingFinished += self.__rewardingFinished
        self.__displayView.viewModel.goToRewardVehicle += self.__goToRewardVehicle
        self.__displayView.viewModel.onCoinApplied += self.__onCoinApplied
        with self.viewModel.transaction() as model:
            model.setExchangeRate(self.__machineConfig.getCoinPrice())
            model.setPurchaseFormState(PurchaseFormState.AVAILABLE if self.__nyMachineController.canBuyCoin else PurchaseFormState.NOT_AVAILABLE)
            self.__nyMachineController.setState(RobotTvScreenState.IDLE)

    def finalize(self):
        self.__nyController.unlockUIControls(id(self))
        self.__nyMachineController.updateSurpriseMachineBusyStatus(False)
        self.__nyMachineController.setState(RobotTvScreenState.IDLE)
        self.__nyMachineController.setViewState(None)
        self.__displayView.viewModel.rewardingFinished -= self.__rewardingFinished
        self.__displayView.viewModel.goToRewardVehicle -= self.__goToRewardVehicle
        self.__displayView.viewModel.onCoinApplied -= self.__onCoinApplied
        self.__displayView.destroyWindow()
        self.__displayView = None
        self.__asyncScope.destroy()
        super(NySurpriseMachineView, self).finalize()
        return

    def setInternalViewState(self, state, skipFlight=None):
        super(NySurpriseMachineView, self).setInternalViewState(state, skipFlight)
        viewState = _INTERNAL_STATE_TO_MACHINE_VIEW.get(state, MachineViews.SPEND_TOKENS)
        self.viewModel.setMachineViews(viewState)
        self.__nyMachineController.setViewState(viewState)

    def _getEvents(self):
        return ((self.__nyMachineController.onMachineButtonPress, self.__onButtonPress),
         (self.__nyMachineController.onMachineButtonHovered, self.__onMachineButtonHovered),
         (self.viewModel.onBuyBtnClick, self.__onBuyBtnClick),
         (self.viewModel.goToMachineMain, self.__onGoToMachineMain),
         (self.viewModel.goToBuyTokens, self.__onGoToBuyTokens),
         (self.viewModel.goToQuest, self.__goToQuest),
         (self.viewModel.onMoveSpace, self.__onMoveSpace),
         (self.viewModel.onMouseOver3dScene, self.__onMouseOver3dScene),
         (self.viewModel.vehicleReward.showVehicle, self.__onShowVehicle),
         (self.viewModel.vehicleReward.closeRewardVehicle, self.__onCloseRewardVehicle),
         (self._nyController.onNySettingsChanged, self.__onNySettingsChanged))

    def preLoad(self, *args, **kwargs):
        super(NySurpriseMachineView, self).preLoad(*args, **kwargs)
        self.__createDisplayView()

    def __onNySettingsChanged(self):
        if self.__machineConfig is not None and not self.__machineConfig.isEnabled():
            self.parentView.destroyWindow()
        return

    def __createDisplayView(self):
        if self.__displayView is None:
            self.__displayView = RobotTvScreenView()
            window = WindowImpl(WindowFlags.SURFACE, content=self.__displayView, layer=WindowLayer.VIEW, name=_TEXTURE_PATH, parent=self.getParentWindow())
            window.load()
        return

    def __onButtonPress(self):
        if self.__nyMachineController.canApplyCoin:
            self.__nyMachineController.setState(RobotTvScreenState.ACTIVE)
            self.setInternalViewState(InternalViewState.MACHINE_REWARDING)
            self.__nyMachineController.updateSurpriseMachineBusyStatus(True)
            NewYearSoundsManager.playEvent(NewYearSoundEvents.MACHINE_BTN_PRESS)
            self.__tryApplyCoin()

    @adisp_process
    def __tryApplyCoin(self):
        lootbox = self.__itemsCache.items.tokens.getLootBoxByID(makeLootboxID(getMachineLootboxToken()))
        if lootbox is None:
            return
        else:
            self.__nyController.lockUIControls(id(self))
            result = yield LootBoxOpenProcessor(lootbox).request()
            if result:
                rewards = None
                if result.success:
                    rewardsList = result.auxData.get('bonus')
                    if rewardsList:
                        rewards = rewardsList[0]
                        self.__sendRewardNotification(rewards)
                    else:
                        self.__nyController.unlockUIControls(id(self))
                        return
                waitEventAndCall(self.__onCoinAppliedEvent, partial(self.__coinApplied, result.success, rewards))
            else:
                self.__nyController.unlockUIControls(id(self))
                SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.machine.server_error.text()), type=SM_TYPE.ErrorHeader, priority='high', messageData={'header': backport.text(R.strings.ny.notification.machine.server_error.header())})
            return

    def __sendRewardNotification(self, rewards):
        SystemMessages.pushMessage(text=backport.text(R.strings.ny.notification.machine.run.text(), time=time_utils.getDateTimeInLocal(time_utils.getCurrentTimestamp()).strftime('%d.%m.%y %H:%M:%S')), type=SM_TYPE.NYSurpriseMachineSingleReward, priority=NotificationPriorityLevel.MEDIUM, messageData={'rewards': QuestAchievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processTokens=False)})

    def __coinApplied(self, success, rewards):
        if success and rewards:
            if isRewardVehicle(rewards):
                self.__nyMachineController.setState(RobotTvScreenState.VEHICLEREWARDING)
                waitEventAndCall(self.__goToRewardVehicleEvent, partial(self.__showVehicle, rewards))
                waitEventAndCall(self.__finishRewardEvent, partial(self.__changeState, InternalViewState.MACHINE_MAIN))
            else:
                self.__nyMachineController.setState(RobotTvScreenState.REWARDING)
                self.__changeState()
            self.__displayView.fillReward(copy.deepcopy(rewards))
        else:
            self.__nyMachineController.setState(RobotTvScreenState.ERROR)
            self.__changeState()
        self.__nyController.unlockUIControls(id(self))

    def __onBuyBtnClick(self, event):
        count = int(event.get('count'))
        self.__buyMachineCoin(count)

    @adisp_process
    @replaceNoneKwargsModel
    def __buyMachineCoin(self, count, model=None):
        result = yield BuyMachineCoinsProcessor(count).request()
        if result and result.success:
            model.setPurchaseFormState(PurchaseFormState.AVAILABLE)
            SystemMessages.pushMessage(priority=result.msgPriority, text=result.userMsg, type=result.sysMsgType, messageData=result.msgData)
        else:
            model.setPurchaseFormState(PurchaseFormState.ERROR)

    def __onGoToBuyTokens(self):
        if not self.__nyMachineController.isMachineBusy:
            self.__nyMachineController.setState(RobotTvScreenState.IDLE)
            self.setInternalViewState(InternalViewState.BUY_MACHINE_COIN)

    def __onGoToMachineMain(self):
        if not self.__nyMachineController.isMachineBusy:
            self.__nyMachineController.setState(RobotTvScreenState.IDLE)
            self.setInternalViewState(InternalViewState.MACHINE_MAIN)

    def __goToQuest(self):
        if not self.__nyMachineController.isMachineBusy:
            self.__newYearNavigation.showNavigationView(ViewAliases.QUESTS_VIEW)

    def __rewardingFinished(self):
        self.__finishRewardEvent.set()

    def __onCoinApplied(self):
        self.__onCoinAppliedEvent.set()

    def __goToRewardVehicle(self):
        self.__goToRewardVehicleEvent.set()

    def __showVehicle(self, rewards):
        vehList = rewards.get('vehicles', [])
        vehIntCD = first(vehList[0].keys()) if vehList else None
        if vehIntCD:
            self.setInternalViewState(InternalViewState.VEHICLE_MACHINE_REWARDING)
            selectVehicleInHangar(vehIntCD, loadHangar=False)
            veh = self.__itemsCache.items.getItemByCD(int(vehIntCD))
            NewYearSoundsManager.playEvent(NewYearSoundEvents.SURPRISE_MACHINE_EXIT)
            NewYearSoundsManager.playEvent(NewYearSoundEvents.HANGAR)
            WWISE.WW_setState(NewYearSoundVars.STATE_NEWYEAR_PLACE, NewYearSoundStates.HANGAR)
            with self.viewModel.vehicleReward.transaction() as model:
                model.setVehicleName(veh.userName)
                model.setVehicleLvl(veh.level)
                model.setVehicleType(veh.type)
                model.setIsElite(veh.isElite)
                model.setIsMainViewVisible(False)
        return

    def __changeState(self, state=None):
        self.__nyMachineController.updateSurpriseMachineBusyStatus(False)
        if state:
            self.setInternalViewState(state)
            self.__nyMachineController.setState(RobotTvScreenState.IDLE)
        self.__finishRewardEvent.clear()
        self.__goToRewardVehicleEvent.clear()
        self.__onCoinAppliedEvent.clear()

    def __onShowVehicle(self):
        self.__nyMachineController.updateSurpriseMachineBusyStatus(False)
        self.__nyMachineController.setState(RobotTvScreenState.IDLE)
        NewYearNavigation.closeMainView(True)

    def __onCloseRewardVehicle(self):
        self.viewModel.vehicleReward.setIsMainViewVisible(True)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.HANGAR_EXIT)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.SURPRISE_MACHINE)
        WWISE.WW_setState(NewYearSoundVars.STATE_NEWYEAR_PLACE, NewYearSoundStates.TOYS)
        self.__rewardingFinished()

    @staticmethod
    def __onMoveSpace(args=None):
        if args is None:
            return
        else:
            dx = args.get('dx')
            dy = args.get('dy')
            dz = args.get('dz')
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': dx,
             'dy': dy,
             'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx={'dx': dx,
             'dy': dy,
             'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
            return

    @staticmethod
    def __onMouseOver3dScene(args):
        if NewYearNavigation.getCurrentViewName() == ViewAliases.SURPRISE_MACHINE_VIEW:
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': bool(args.get('isOver3dScene'))}))

    def __onMachineButtonHovered(self, isHovered):
        self.viewModel.setIsBtnHovered(isHovered)
