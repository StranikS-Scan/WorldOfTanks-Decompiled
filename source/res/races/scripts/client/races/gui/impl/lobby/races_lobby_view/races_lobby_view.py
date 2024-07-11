# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/lobby/races_lobby_view/races_lobby_view.py
import copy
import logging
import typing
import adisp
from gui_lootboxes.gui.shared.event_dispatcher import showStorageView
from races.gui.impl.gen.view_models.views.lobby.races_lobby_view.progression_tooltip_model import ProgressionTooltipModel
from races.gui.impl.gen.view_models.views.lobby.races_lobby_view.races_lobby_view_model import RacesLobbyViewModel
from races.gui.impl.gen.view_models.views.lobby.vehicles_carousel.races_vehicle_info_model import RacesVehicleInfoModel
from races.gui.impl.lobby.races_lobby_view.tth_tooltip import TthTooltip
from races.gui.impl.lobby.races_lobby_view.races_progression_view import getRacesBonusPacker
from races.gui.impl.lobby.vehicles_carousel.tank_tooltip import TankTooltip
from races.gui.shared.event_dispatcher import showRacesProgressionView, showRacesIntro
from races.skeletons.progression_controller import IRacesProgressionController
from races.gui.shared.bonus_helpers import sortBonuses
from CurrentVehicle import g_currentVehicle
from account_helpers.AccountSettings import LOOT_BOXES_VIEWED_COUNT, LOOT_BOXES_KEY_VIEWED_COUNT, LOOT_BOXES_VIEWED_HAS_INFINITE, RACES_INTRO_SCREEN_SHOWN
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer
from frameworks.wulf.view.array import fillIntsArray
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.sounds.filters import StatesGroup, States
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IRacesBattleController, IGuiLootBoxesController
from skeletons.gui.shared import IItemsCache
from sound_gui_manager import CommonSoundSpaceSettings
from gui_lootboxes.gui.storage_context.context import ReturnPlaces
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from frameworks.wulf.view.view import View
    from frameworks.wulf.view.view_event import ViewEvent
_logger = logging.getLogger(__name__)
MAX_STAGE_PROGRESSION = 9
_PEDESTAL_REWARDS_COUNT = 3

class RacesLobbyView(ViewImpl, LobbyHeaderVisibility):
    __slots__ = ('__selectedRacesTank',)
    _SOUND_STATE_PLACE = 'STATE_hangar_place'
    _SOUND_STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name='racesLobbyView', entranceStates={_SOUND_STATE_PLACE: _SOUND_STATE_PLACE_GARAGE,
     StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
    __racesCtrl = dependency.descriptor(IRacesBattleController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    __progressionCtrl = dependency.descriptor(IRacesProgressionController)
    __appLoader = dependency.descriptor(IAppLoader)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = RacesLobbyViewModel()
        super(RacesLobbyView, self).__init__(settings)
        self.__racesCtrl.saveLastSelectedRegularVehicle()
        self.__selectedRacesTank = self.__racesCtrl.getLastSelectedTank()

    @property
    def viewModel(self):
        return super(RacesLobbyView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RacesLobbyView, self)._onLoading(*args, **kwargs)
        self.__updateCarouselModel()
        self.__lobbyContext.addHeaderNavigationConfirmator(self.__handleHeaderNavigation)
        self.__updateSelectedVehicle()
        self.viewModel.lootboxEntryModel.setIsVisible(self.__guiLootBoxes.isEnabled())
        self.viewModel.lootboxEntryModel.setIsLootBoxesEnabled(self.__guiLootBoxes.isLootBoxesAvailable())
        self.__updateLootboxEntryModel(self.__guiLootBoxes.getBoxesCount())
        self.__updateProgressionWidget()
        if not self.__racesCtrl.getRacesAccountSettings(RACES_INTRO_SCREEN_SHOWN):
            showRacesIntro(self.getParentWindow())

    def _initialize(self, *args, **kwargs):
        super(RacesLobbyView, self)._initialize(*args, **kwargs)
        app = self.__appLoader.getApp()
        app.setBackgroundAlpha(0)

    def _finalize(self):
        self.__lobbyContext.deleteHeaderNavigationConfirmator(self.__handleHeaderNavigation)
        super(RacesLobbyView, self)._finalize()

    @adisp.adisp_async
    def __handleHeaderNavigation(self, callback, alias=None):
        if alias == VIEW_ALIAS.LOBBY_HANGAR:
            callback(False)
        callback(True)

    def _getEvents(self):
        return ((self.viewModel.onMoveSpace, self._onMoveSpace),
         (self.viewModel.onAboutEvent, self.__onAboutEvent),
         (self.viewModel.onEscapePressed, self.__onEscapePressed),
         (self.viewModel.vehiclesCarouselModel.onVehicleSelect, self.__onVehicleSelect),
         (self.__guiLootBoxes.onBoxesCountChange, self.__updateBoxesCount),
         (self.__guiLootBoxes.onKeysUpdate, self.__onKeysUpdate),
         (self.__guiLootBoxes.onAvailabilityChange, self.__onLootboxAvailabilityChange),
         (self.__guiLootBoxes.onStatusChange, self.__onLootboxStatusChange),
         (self.viewModel.lootboxEntryModel.onOpenStorage, self.__onOpenLootboxStorage),
         (self.__progressionCtrl.onProgressPointsUpdated, self.__updateProgressionWidget),
         (self.viewModel.progressionWidgetModel.onOpenProgression, self.__openProgressionView),
         (self.__itemsCache.onSyncCompleted, self.__updateCarouselModel))

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.races.lobby.races_lobby_view.VehicleTooltip():
            slotId = int(event.getArgument('slotId'))
            inBattle = bool(event.getArgument('inBattle'))
            vehiclesInfo = self.__racesCtrl.getRacesVehiclesInfo()
            vehiclesList = sorted(vehiclesInfo.items(), key=lambda item: item[1]['order'])
            vehCompDescr = vehiclesList[slotId][0]
            vehicleTth = vehiclesInfo.get(vehCompDescr)['vehicleTth']
            vehicle = self.__itemsCache.items.getItemByCD(vehCompDescr)
            return TankTooltip(slotId, vehicle, inBattle, vehicleTth)
        if contentID == R.views.races.lobby.races_lobby_view.TTHTooltip():
            return TthTooltip(int(event.getArgument('property') or 0))
        if contentID == R.views.races.lobby.races_lobby_view.ProgressionTooltip():
            settings = ViewSettings(layoutID=R.views.races.lobby.races_lobby_view.ProgressionTooltip(), model=ProgressionTooltipModel())
            self.__fillProgresionTooltiopModel(settings.model)
            return ViewImpl(settings)

    def __updateCarouselModel(self, *_):
        availiableVehicles = self.__racesCtrl.getRacesVehicles()
        with self.viewModel.vehiclesCarouselModel.transaction() as model:
            vehiclesInfoArray = model.getVehiclesInfo()
            vehiclesInfoArray.clear()
            for vehCompDescr in availiableVehicles:
                vehicle = self.__itemsCache.items.getItemByCD(vehCompDescr)
                vehicleInfo = RacesVehicleInfoModel()
                vehicleInfo.setVehicleName(getNationLessName(vehicle.name))
                vehicleInfo.setVehicleUserName(vehicle.shortUserName)
                vehicleInfo.setTooltipName(vehicle.shortUserName)
                vehicleInfo.setInBattle(vehicle.isInBattle)
                self.__fillVehicleTth(vehicleInfo, vehCompDescr)
                vehiclesInfoArray.addViewModel(vehicleInfo)

            vehiclesInfoArray.invalidate()

    def __onVehicleSelect(self, args):
        self.__selectedRacesTank = int(args.get('id'))
        self.__racesCtrl.setLastSelectedTank(self.__selectedRacesTank)
        self.__updateSelectedVehicle()

    def __updateSelectedVehicle(self):
        vehCompDescr = self.__racesCtrl.getSelectedRacesVehicleDescr()
        vehicle = self.__itemsCache.items.getItemByCD(vehCompDescr)
        if vehicle is not None:
            g_currentVehicle.selectVehicle(vehicle.invID)
        else:
            _logger.warning('[RacesLobbyView] Can not select vehicle')
        vehicleNationLessName = getNationLessName(vehicle.name)
        with self.viewModel.vehiclesCarouselModel.transaction() as model:
            model.setVehicleName(vehicleNationLessName)
            model.setVehicleUserName(vehicle.shortUserName)
        return

    def _onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            ctx = {'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')}
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx=ctx), EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx=ctx), EVENT_BUS_SCOPE.GLOBAL)
            return

    def __onEscapePressed(self):
        dialogsContainer = self.__appLoader.getApp().containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onAboutEvent(self):
        url = GUI_SETTINGS.infoPageRaces
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def __onOpenLootboxStorage(self):
        if self.__guiLootBoxes.isLootBoxesAvailable():
            showStorageView(returnPlace=ReturnPlaces.TO_CUSTOM)
            self.viewModel.lootboxEntryModel.setHasNew(False)
            self.__guiLootBoxes.setSetting(LOOT_BOXES_VIEWED_COUNT, self.__guiLootBoxes.getBoxesCount())
            self.__guiLootBoxes.setSetting(LOOT_BOXES_KEY_VIEWED_COUNT, self.__guiLootBoxes.getBoxKeysCount())
            self.__guiLootBoxes.setSetting(LOOT_BOXES_VIEWED_HAS_INFINITE, self.__guiLootBoxes.hasInfiniteLootboxes())

    def __updateBoxesCount(self, count, *_):
        self.__updateLootboxEntryModel(count)

    def __onKeysUpdate(self, *_):
        self.__updateLootboxEntryModel(self.__guiLootBoxes.getBoxesCount())

    def __updateLootboxEntryModel(self, boxCount):
        lastBoxesViewed = self.__guiLootBoxes.getSetting(LOOT_BOXES_VIEWED_COUNT)
        lastKeysViewed = self.__guiLootBoxes.getSetting(LOOT_BOXES_KEY_VIEWED_COUNT)
        isViewvedHasInfinite = self.__guiLootBoxes.getSetting(LOOT_BOXES_VIEWED_HAS_INFINITE)
        keyCount = self.__guiLootBoxes.getBoxKeysCount()
        hasInfinite = self.__guiLootBoxes.hasInfiniteLootboxes()
        hasNew = boxCount > lastBoxesViewed or keyCount > lastKeysViewed or hasInfinite and hasInfinite != isViewvedHasInfinite
        with self.viewModel.lootboxEntryModel.transaction() as model:
            model.setBoxesCount(boxCount)
            model.setHasNew(hasNew)
            model.setHasInfinite(hasInfinite)

    def __onLootboxAvailabilityChange(self, *_):
        self.viewModel.lootboxEntryModel.setIsLootBoxesEnabled(self.__guiLootBoxes.isLootBoxesAvailable())

    def __onLootboxStatusChange(self, *_):
        self.viewModel.lootboxEntryModel.setIsVisible(self.__guiLootBoxes.isEnabled())

    def __updateProgressionWidget(self):
        with self.viewModel.progressionWidgetModel.transaction() as model:
            currentPoints, stage, maxPoint = self.__progressionCtrl.getProgression()
            model.setCurrentPoints(currentPoints)
            model.setProgressionLevel(stage)
            model.setIsProgressionFinished(maxPoint <= currentPoints)

    def __fillCurrentLevelRewards(self, model):
        packerFactory = getRacesBonusPacker()
        currentStage = self.__progressionCtrl.getCurrentStage()
        currentStage = min(currentStage, MAX_STAGE_PROGRESSION)
        currentBonuses = sortBonuses(self.__progressionCtrl.getBonuses()[currentStage][1])
        if len(currentBonuses) == _PEDESTAL_REWARDS_COUNT:
            currentBonuses[0], currentBonuses[1] = currentBonuses[1], currentBonuses[0]
        rewardsList = model.getCurrentLevelRewards()
        packBonusModelAndTooltipData(currentBonuses, rewardsList, {}, packerFactory)
        rewardsList.invalidate()

    def __openProgressionView(self):
        showRacesProgressionView()

    def __fillVehicleTth(self, vehicleInfoModel, vehCompDescr):
        vehiclePropertyArr = vehicleInfoModel.getVehiclePropertyArray()
        tth = self.__racesCtrl.getRacesVehiclesInfo().get(vehCompDescr)['vehicleTth']
        fillIntsArray(tth, vehiclePropertyArr)
        vehiclePropertyArr.invalidate()

    def __fillProgresionTooltiopModel(self, model):
        scorePoint = []
        finishConfig = copy.copy(self.__racesCtrl.getModeSettings().scoreSystem['finishConfig'])
        scorePoint.extend(finishConfig['position'])
        scorePoint.append(finishConfig['finished'])
        scorePoint.extend([0, 0])
        self.__fillCurrentLevelRewards(model)
        currentPoints, stage, maxPoint = self.__progressionCtrl.getProgression()
        model.setCurrentPoints(currentPoints)
        model.setProgressionLevel(min(stage, MAX_STAGE_PROGRESSION))
        model.setIsProgressionFinished(maxPoint <= currentPoints)
        fillIntsArray(scorePoint, model.getScorePoint())
