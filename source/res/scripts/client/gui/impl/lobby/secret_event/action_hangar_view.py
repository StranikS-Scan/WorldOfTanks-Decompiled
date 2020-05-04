# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/action_hangar_view.py
import logging
import typing
import Event
from PlayerEvents import g_playerEvents
from SE20SelectableObjectTooltipController import SE20SelectableObjectTooltipController
from account_helpers import AccountSettings
from account_helpers.AccountSettings import SECRET_EVENT_2020_SEEN, SECRET_EVENT_BERLIN_2020_SEEN
from adisp import process
from constants import PREBATTLE_TYPE
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.lobby_vehicle_marker_view import LOBBY_TYPE
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.app_loader import sf_lobby
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.secret_event.action_hangar_model import ActionHangarModel
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.characteristics_advantage_model import CharacteristicsAdvantageModel
from gui.impl.gen.view_models.views.lobby.secret_event.general_model import GeneralModel
from gui.impl.gen.view_models.views.lobby.secret_event.general_tooltip_model import GeneralTooltipModel
from gui.impl.gen.view_models.views.lobby.secret_event.order_model import OrderModel
from gui.impl.lobby.secret_event import RewardListMixin, ProgressMixin, AbilitiesMixin, EventViewMixin, EnergyMixin, VehicleMixin, ViewModelRestoreMixin
from gui.impl.lobby.secret_event.action_view_with_menu import ActionViewWithMenu
from gui.impl.lobby.secret_event.general_info_tip import GeneralInfoTip
from gui.impl.lobby.secret_event.sound_constants import ACTION_HANGAR_SETTINGS
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.events_dispatcher import showOrderSelectView
from gui.server_events.game_event import BattleResultsOpenMixin
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.gui_items import GUI_ITEM_TYPE
from hangar_selectable_objects import ISelectableLogicCallback, HangarSelectableLogic
from helpers import dependency, isPlayerAccount
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from frameworks.wulf.gui_constants import ViewStatus
if typing.TYPE_CHECKING:
    from gui.server_events.game_event.commander_event_progress import CommanderEventProgress
    from gui.impl.gen.view_models.views.lobby.secret_event.characteristics_model import CharacteristicsModel
_logger = logging.getLogger(__name__)
_NOTIFICATIONS_BOTTOM_PADDING = 128

class ActionHangarView(ActionViewWithMenu, ISelectableLogicCallback, RewardListMixin, ProgressMixin, ViewModelRestoreMixin, AbilitiesMixin, EventViewMixin, EnergyMixin, VehicleMixin, SE20SelectableObjectTooltipController, IGlobalListener, CallbackDelayer, BattleResultsOpenMixin):
    onEvenetHangarLoaded = Event.Event()
    hangarSpace = dependency.descriptor(IHangarSpace)
    gameEventController = dependency.descriptor(IGameEventController)
    appLoader = dependency.descriptor(IAppLoader)
    itemsCache = dependency.descriptor(IItemsCache)
    _STRENGTH_PREFIX = 'good_{}'
    _WEAKNESS_PREFIX = 'bad_{}'
    ABILITY_TOOLTIP_EVENTS = (TOOLTIPS_CONSTANTS.COMMANDER_RESPAWN_INFO, TOOLTIPS_CONSTANTS.COMMANDER_ABILITY_INFO, TOOLTIPS_CONSTANTS.COMMANDER_CHARACTERISTICS)
    _COMMON_SOUND_SPACE = ACTION_HANGAR_SETTINGS
    _SYNC_WAIT_TIME = 1.0

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        model = self.getViewModelForRestore()
        if model is None:
            model = ActionHangarModel()
        settings.model = model
        self.__selectableLogic = None
        super(ActionHangarView, self).__init__(settings)
        CallbackDelayer.__init__(self)
        ViewModelRestoreMixin.__init__(self)
        return

    @property
    def viewModel(self):
        return self.tempModel or self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = None
            if 'rewardTooltip' in tooltipId:
                window = RewardListMixin.createToolTip(self, event)
            elif tooltipId in self.ABILITY_TOOLTIP_EVENTS or tooltipId == TOOLTIPS_CONSTANTS.EVENT_SQUAD_GENERAL_INFO:
                window = self._createSkillToolTip(event)
            if window is None:
                specialArgs = []
                tankId = event.getArgument('tankId', None)
                tooltipId = event.getArgument('tooltipId', None)
                if tankId is not None:
                    specialArgs = [int(tankId)]
                    tooltipId = TOOLTIPS_CONSTANTS.EVENT_VEHICLE
                elif tooltipId == 'orderTooltip':
                    tooltipId = TOOLTIPS_CONSTANTS.EVENT_BONUSES_INFO
                    specialArgs = [event.getArgument('id')]
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs), self.getParentWindow())
                window.load()
            return window
        else:
            return super(ActionHangarView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return GeneralInfoTip(event.contentID, event.getArgument('id', self.gameEventController.getSelectedCommanderID()), event.getArgument('type', GeneralTooltipModel.DEFAULT)) if event.contentID == R.views.lobby.secretEvent.GeneralTooltip() else None

    def onHighlight3DEntity(self, entity):
        tooltipMgr = self.appLoader.getApp().getToolTipMgr()
        itemId = entity.selectionId
        if not itemId or tooltipMgr is None:
            return
        else:
            lobbySubContainer = self.__app.containerManager.getContainer(ViewTypes.LOBBY_TOP_SUB)
            if lobbySubContainer is not None:
                if lobbySubContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.EVENT_BATTLE_RESULTS}):
                    return
            self._onHighlight3DEntity(tooltipMgr, entity)
            return

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.__fillGenerals()

    def onPrbEntitySwitched(self):
        self.__fillGenerals()

    def onFade3DEntity(self, entity):
        self._onFade3DEntity(self.appLoader.getApp().getToolTipMgr(), entity)

    def _initialize(self, *args, **kwargs):
        super(ActionHangarView, self)._initialize()
        app = self.appLoader.getApp()
        if app is not None:
            app.setBackgroundAlpha(0.0)
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.LOBBY_TYPE_CHANGED, ctx={'lobbyType': LOBBY_TYPE.EVENT}), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(events.LobbyNotificationEvent(events.LobbyNotificationEvent.SET_BOTTOM_PADDING, _NOTIFICATIONS_BOTTOM_PADDING), scope=EVENT_BUS_SCOPE.LOBBY)
        self._readInterfaceScale()
        self.__addListeners()
        return

    def _onLoading(self, *args, **kwargs):
        super(ActionHangarView, self)._onLoading()
        self.__fillViewModel()
        if self.__selectableLogic is None:
            self.__selectableLogic = self._createSelectableLogic()
            self.__selectableLogic.init(self)
        return

    def _onLoaded(self, *args, **kwargs):
        super(ActionHangarView, self)._onLoaded(*args, **kwargs)
        isAssault = self.gameEventController.isBerlinStarted()
        if isAssault:
            AccountSettings.setCounters(SECRET_EVENT_BERLIN_2020_SEEN, True)
        else:
            AccountSettings.setCounters(SECRET_EVENT_2020_SEEN, True)
        self.onEvenetHangarLoaded()

    def _finalize(self):
        self.stopCallback(self.__onSyncCompleted)
        if isPlayerAccount():
            self.saveViewModel(ActionHangarModel, self.__fillViewModel)
        self.__removeListeners()
        if self.__selectableLogic is not None:
            self.__selectableLogic.fini()
            self.__selectableLogic = None
        g_eventBus.handleEvent(events.LobbyNotificationEvent(events.LobbyNotificationEvent.SET_BOTTOM_PADDING, 0), scope=EVENT_BUS_SCOPE.LOBBY)
        super(ActionHangarView, self)._finalize()
        return

    def _onMoveSpace(self, args=None):
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

    def _onCursorOver3DScene(self, args=None):
        if args is None:
            _logger.error("Can't notified cursor over changed. args=None. Please fix JS")
            return
        else:
            isOver3dScene = args.get('isOver3dScene', False)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': isOver3dScene}), EVENT_BUS_SCOPE.DEFAULT)
            self.hangarSpace.setVehicleSelectable(isOver3dScene)
            return

    def _createSelectableLogic(self):
        return HangarSelectableLogic()

    def __canChangeVehicle(self):
        if self.prbDispatcher is not None:
            permission = self.prbDispatcher.getGUIPermissions()
            if permission is not None:
                return permission.canChangeVehicle()
        return True

    def _onSelectGeneralChanged(self, args=None):
        if not self.__canChangeVehicle():
            return
        else:
            if args is not None:
                generalId = int(args.get('id'))
                self.__fillGeneralProgress(generalId)
                self.__fillGeneralCharacteristics(generalId)
                generals = self.viewModel.generals.getItems()
                for general in generals:
                    general.setIsSelected(general.getId() == generalId)

                self.viewModel.setSelectedGeneralId(generalId)
                self.gameEventController.setSelectedCommanderID(generalId)
                self.__fillOrder()
            else:
                _logger.error("Can't change selected general. args=None. Please fix JS")
            return

    def _onClose(self):
        self.__doSelectAction(actionName=PREBATTLE_ACTION_NAME.RANDOM)

    def _addWeaknesses(self, commander, model):
        model.cons.clearItems()
        weaknesses = commander.getWeaknessesByLevel(commander.getCurrentProgressLevel())
        for id_, weakness in enumerate(weaknesses):
            item = self._composeCharacteristicItem(id_, weakness, self._WEAKNESS_PREFIX)
            model.cons.addViewModel(item)

        model.cons.invalidate()

    def _addStrength(self, commander, model):
        model.pros.clearItems()
        strengths = commander.getStrengthByLevel(commander.getCurrentProgressLevel())
        for id_, strength in enumerate(strengths):
            item = self._composeCharacteristicItem(id_, strength, self._STRENGTH_PREFIX)
            model.pros.addViewModel(item)

        model.pros.invalidate()

    def _composeCharacteristicItem(self, id_, name, typePrefix):
        item = CharacteristicsAdvantageModel()
        item.setId(id_)
        item.setCharName(name)
        item.setPrefix(typePrefix)
        characterNameItem = R.strings.event.tank_params.dyn(name)
        if characterNameItem is not None and characterNameItem.exists():
            item.setText(characterNameItem())
        item.setIcon(R.images.gui.maps.icons.secretEvent.vehParams.dyn(typePrefix.format(name), R.images.gui.maps.icons.secretEvent.vehParams.noImage)())
        return item

    def _createSkillToolTip(self, event):
        window = BackportTooltipWindow(createTooltipData(specialAlias=event.getArgument('tooltipId'), isSpecial=True, specialArgs=[event.getArgument('key'), event.getArgument('prefix', '')]), self.getParentWindow())
        window.load()
        return window

    def __onShopUpdated(self):
        self.__fillGenerals()
        self.__fillOrder()

    def __onCacheResync(self, _, diff):
        if GUI_ITEM_TYPE.VEHICLE in diff:
            if not self.__canChangeVehicle():
                pass

    def __addListeners(self):
        self.viewModel.onMoveSpace += self._onMoveSpace
        self.viewModel.onSelectGeneralChanged += self._onSelectGeneralChanged
        self.viewModel.onClose += self._onClose
        self.eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.viewModel.onCursorOver3DScene += self._onCursorOver3DScene
        self.viewModel.onBuyOrderClick += self.__onBuyOrderClick
        g_playerEvents.onGeneralLockChanged += self.__onSyncCompleted
        self.gameEventController.getShop().onShopUpdated += self.__onShopUpdated
        self._eventCacheSubscribe()
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self._settingsCore.interfaceScale.onScaleChanged += self._readInterfaceScale
        self.startGlobalListening()

    def __removeListeners(self):
        self.stopGlobalListening()
        self.viewModel.onMoveSpace -= self._onMoveSpace
        self.viewModel.onSelectGeneralChanged -= self._onSelectGeneralChanged
        self.viewModel.onClose -= self._onClose
        self.eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self.viewModel.onCursorOver3DScene -= self._onCursorOver3DScene
        self.viewModel.onBuyOrderClick -= self.__onBuyOrderClick
        g_playerEvents.onGeneralLockChanged -= self.__onSyncCompleted
        self.gameEventController.getShop().onShopUpdated -= self.__onShopUpdated
        self._eventCacheUnsubscribe()
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self._settingsCore.interfaceScale.onScaleChanged -= self._readInterfaceScale

    def __fillViewModel(self):
        if self.getViewModelForRestore() is not None and self.viewStatus not in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
            self.saveViewModelForRestore(None)
            self.delayCallback(self._SYNC_WAIT_TIME, self.__onSyncCompleted)
            return
        else:
            self.viewModel.setCurrentView(ActionMenuModel.BASE)
            selectedGeneralId = self.gameEventController.getSelectedCommanderID()
            self.__fillGenerals()
            self.__fillActionProgress()
            self.__fillGeneralProgress(selectedGeneralId)
            self.__fillGeneralCharacteristics(selectedGeneralId)
            self.__fillOrder()
            return

    def __createOrder(self, orderData):
        order = OrderModel()
        order.setIcon(orderData.hangarIcon96x96)
        order.setCount(orderData.currentCount)
        order.setIsSelected(orderData.isSelected)
        order.setTimer(orderData.nextRechargeTime)
        order.setId(orderData.id_)
        order.setTooltipId(orderData.tooltipId)
        order.setRechargeCount(orderData.nextRechargeCount)
        order.setType(orderData.orderType)
        if orderData.orderType == OrderModel.EXCHANGE:
            shopItem = self.gameEventController.getShop().getExchangePackOfGeneral(self.gameEventController.getSelectedCommanderID())
            if shopItem:
                order.setIsTokenShortage(shopItem.isTokenShortage)
            else:
                order.setType(OrderModel.TIMER)
        return order

    def __fillOrder(self):
        vm = self.viewModel
        vm.orders.clearItems()
        commander = self.gameEventController.getSelectedCommander()
        refillOrder = self.getEnergyData(commander, commander.getRefillEnergyID(), OrderModel.TIMER)
        buyableOrder = self.getEnergyData(commander, commander.getBuyEnergyID(), OrderModel.BUY)
        questOrder = self.getEnergyData(commander, commander.getQuestEnergyID(), OrderModel.EXCHANGE)
        vm.orders.addViewModel(self.__createOrder(refillOrder))
        vm.orders.addViewModel(self.__createOrder(buyableOrder))
        vm.orders.addViewModel(self.__createOrder(questOrder))
        vm.orders.invalidate()

    def __fillActionProgress(self):
        progressionData = self.getCurrentProgressionData(self.gameEventController.getCurrentFront(), False)
        with self.viewModel.actionProgress.transaction() as actionProgress:
            actionProgress.setIcon(R.invalid())
            actionProgress.setProgressMax(progressionData.maxProgress)
            actionProgress.setProgress(progressionData.currentProgress)
            actionProgress.setLevel(progressionData.level)
            actionProgress.rewardList.clearItems()
            self.fillStubRewardList(actionProgress.rewardList, self.getRewards(progressionData.gameEventItem, progressionData.level, iconSizes=(AWARDS_SIZES.SMALL, AWARDS_SIZES.BIG)), progressionData.isCompleted, progressionData.level)

    def __fillGeneralProgress(self, generalId):
        commander = self.__getCommander(generalId)
        progressionData = self.getCurrentProgressionData(commander)
        level = progressionData.level if not progressionData.isCompleted else commander.getRealMaxLevel()
        vehicleData = self.getVehicleDataByLevel(commander, level if not progressionData.isCompleted else level - 1)
        with self.viewModel.generalProgress.transaction() as generalProgress:
            generalProgress.setId(generalId)
            generalProgress.setName(R.strings.event.unit.name.num(generalId)())
            generalProgress.setDescription(R.strings.event.unit.description.num(generalId)())
            generalProgress.setProgressMax(progressionData.maxProgress)
            generalProgress.setProgress(progressionData.currentProgress)
            generalProgress.setLevel(level)
            generalProgress.abilities.clearItems()
            self.fillAbilitiesList(generalProgress.abilities, commander, None, level)
            vehicleIconName = vehicleData.vehicle.name.split(':', 1)[-1].replace('-', '_')
            generalProgress.prizeTank.setTankIcon(R.images.gui.maps.icons.secretEvent.vehicles.c_48x48.dyn(vehicleIconName)())
            generalProgress.prizeTank.setTankId(vehicleData.typeCompDescr)
            generalProgress.prizeTank.setIsComplete(progressionData.isCompleted)
            generalProgress.setIsComplete(progressionData.isCompleted)
        return

    def __fillGeneralCharacteristics(self, generalId):
        commander = self.gameEventController.getCommander(generalId)
        with self.viewModel.characteristics.transaction() as model:
            self._addWeaknesses(commander, model)
            self._addStrength(commander, model)
            self.fillAbilitiesList(model.skills, commander)

    def __fillGenerals(self):
        generals = self.viewModel.generals
        generals.clearItems()
        for id_ in self.gameEventController.getCommanders():
            commander = self.gameEventController.getCommander(id_)
            general = GeneralModel()
            level = commander.getCurrentProgressLevel()
            currentEnergy = commander.getCurrentEnergy()
            with general.transaction() as gTrx:
                vehicle = commander.getVehicleByLevel(level)
                gTrx.setId(id_)
                gTrx.setLabel(R.strings.event.unit.name.num(id_)())
                gTrx.setIsInBattle(commander.isLocked())
                isSelected = id_ == self.gameEventController.getSelectedCommanderID()
                gTrx.setIsInPlatoon(self.prbDispatcher.getFunctionalState().entityTypeID == PREBATTLE_TYPE.EVENT and self.prbDispatcher.getPlayerInfo().isReady and isSelected)
                gTrx.setIsSelected(isSelected)
                gTrx.setLevel(str(level + 1))
                gTrx.setVehicleType(vehicle.type)
                progressionData = self.getCurrentProgressionData(commander)
                gTrx.setCurrentProgress(progressionData.currentProgress)
                gTrx.setMaxProgress(progressionData.maxProgress)
                vehicleIconName = vehicle.name.split(':', 1)[-1].replace('-', '_')
                gTrx.setVehicleIcon(R.images.gui.maps.icons.secretEvent.vehicles.c_160x100_carousel.dyn(vehicleIconName)())
                if currentEnergy:
                    gTrx.setOrderLabel(currentEnergy.getLabel())
            generals.addViewModel(general)
            generals.invalidate()

    @sf_lobby
    def __app(self):
        return None

    @process
    def __doSelectAction(self, actionName=None):
        if actionName is not None:
            yield self.prbDispatcher.doSelectAction(PrbAction(actionName))
            return
        else:
            self.showMission(self.getBattleQuestData(self.gameEventController.getSelectedCommander().getQuestEnergyID()), self.viewModel.getCurrentView())
            return

    def __onSyncCompleted(self):
        if self.isBattleResultsOpen:
            self.delayCallback(self._SYNC_WAIT_TIME, self.__onSyncCompleted)
        else:
            self.stopCallback(self.__onSyncCompleted)
            selectedCommanderID = self.gameEventController.getSelectedCommanderID()
            self.__fillActionProgress()
            self.__fillGeneralCharacteristics(selectedCommanderID)
            self.__fillGeneralProgress(selectedCommanderID)
            self.viewModel.generals.clearItems()
            self.__fillGenerals()
            self.__fillOrder()
            self.viewModel.generals.invalidate()

    def __onBuyOrderClick(self, args=None):
        if args is None:
            _logger.error('args=None. Please fix JS')
            return
        else:
            isBuy = args.get('isBuy')
            showOrderSelectView(isExchange=not isBuy)
            return

    def __getCommander(self, commanderId):
        return self.gameEventController.getCommander(commanderId)
