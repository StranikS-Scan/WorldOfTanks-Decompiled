# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/portal_lobby_view.py
from constants import PREBATTLE_TYPE
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from portal.gui.impl.lobby.tooltips.abilities_tooltip import AbilitiesTooltip
from portal.gui.impl.lobby.tooltips.vehicle_tooltip import VehicleTooltip
from portal.gui.impl.lobby.tooltips.shell_tooltip import ShellTooltip
from portal.gui.impl.lobby.tooltips.repair_kit_tooltip import RepairKitTooltip
from portal.gui.impl.lobby.tooltips.complexity_tooltip import ComplexityTooltip
from frameworks.wulf import ViewFlags, ViewSettings
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from frameworks.wulf import Array
from helpers import dependency
from portal.gui.impl.gen.view_models.views.lobby.portal_lobby_view_model import PortalLobbyViewModel
from portal.skeletons.portal_event_controller import IPortalEventController
from portal.sounds.sound_constants import PORTAL_LOBBY_SOUND_SPACE
from skeletons.gui.shared import IItemsCache
from skeletons.gui.app_loader import IAppLoader
from gui.shared.gui_items.Vehicle import getIconResourceName, Vehicle
from portal.gui.impl.gen.view_models.views.lobby.portal_carousel_tank_model import PortalCarouselTankModel
from CurrentVehicle import g_currentVehicle
from portal.gui.impl.gen.view_models.views.lobby.portal_complexity_level import PortalComplexityLevel
from gui.shared.event_dispatcher import showShop
from portal.gui.shared.event_dispatcher import showPortalProgressionView, showPortalInfoPage
from portal.gui.shared.event_dispatcher import showPortalUpgradeView
from portal.gui.portal_event_helpers import getShopPageURL
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from PlayerEvents import g_playerEvents
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from portal_common.portal_constants import PortalBattleLevel
from portal_account_settings import getMaxViewedUnlockedUpgradeLevel
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState

class PortalLobby(InjectComponentAdaptor):

    def _makeInjectView(self):
        return PortalLobbyView(R.views.portal.lobby.PortalLobbyView())


class PortalLobbyView(ViewImpl):
    __slots__ = ()
    __portalController = dependency.descriptor(IPortalEventController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __appLoader = dependency.descriptor(IAppLoader)
    _COMMON_SOUND_SPACE = PORTAL_LOBBY_SOUND_SPACE

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PortalLobbyViewModel()
        super(PortalLobbyView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PortalLobbyView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.portal.lobby.tooltips.AbilitiesTooltip():
            name = event.getArgument('name', 'default')
            return AbilitiesTooltip(name)
        if contentID == R.views.portal.lobby.tooltips.VehicleTooltip():
            vehicleId = event.getArgument('vehicleId', 'default')
            return VehicleTooltip(vehicleId)
        if contentID == R.views.portal.lobby.tooltips.ShellTooltip():
            return ShellTooltip(self.__portalController.getCurrentSelectedVehicle())
        if contentID == R.views.portal.lobby.tooltips.RepairKitTooltip():
            return RepairKitTooltip()
        if contentID == R.views.portal.lobby.tooltips.ComplexityTooltip():
            level = event.getArgument('level')
            isLocked = self.__portalController.isComplexityLevelLocked(level)
            vehicleLvl = self.__portalController.getComplexityRecommendedVehicleLvl(level)
            return ComplexityTooltip(level, isLocked, vehicleLvl)
        return super(PortalLobbyView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(PortalLobbyView, self)._onLoading(*args, **kwargs)
        self._updateModel()

    def _onLoaded(self, *args, **kwargs):
        self.updateVisibilityHangarHeaderMenu(isVisible=False)

    def _finalize(self):
        self.updateVisibilityHangarHeaderMenu(isVisible=True)
        super(PortalLobbyView, self)._finalize()

    def _updateModel(self):
        with self.viewModel.transaction() as model:
            self.__fillModel(model)
        self.__updateSquadState()

    def __fillModel(self, model):
        self._fillVehicles(model.tanks)
        self._fillComplexityLevels(model.complexityLevelWidget.levels)
        self._fillAmmunitionPanel(model.portalAmmunitionPanel)
        self._fillPortalQuestWidget(model.portalQuestWidget)

    def _fillAmmunitionPanel(self, model):
        item = self.__portalController.getCurrentSelectedVehicle()
        model.setShellType(item.shells.installed[0].type)
        abilities = Array()
        for abilityName in self.__portalController.getVehicleAbilities(item):
            abilities.addString(abilityName)

        model.setAbilities(abilities)
        currentLevel = self.__portalController.getMaxUnlockedLevel(item)
        viewedLevel = getMaxViewedUnlockedUpgradeLevel(item.intCD)
        model.setHasNewUpgrade(currentLevel > viewedLevel)

    def _fillComplexityLevels(self, array):
        array.clearItems()
        for level in list(PortalBattleLevel)[1:]:
            model = PortalComplexityLevel()
            model.setLevel(level)
            model.setStatus(self.__portalController.getComplexityLevelStatus(level))
            array.addViewModel(model)

        array.invalidate()

    def _fillVehicles(self, array):
        item = self.__portalController.getCurrentSelectedVehicle()
        vehicles = self.__portalController.getOrderedPortalVehicles()
        array.clearItems()
        for vehicle in vehicles:
            iconName = getIconResourceName(vehicle.name)
            vehicleState, _ = vehicle.getState()
            model = PortalCarouselTankModel()
            model.setTitle(vehicle.userName)
            model.setIcon(iconName)
            model.setId(vehicle.invID)
            model.setSelected(vehicle == item)
            model.setInBattle(vehicle.isInBattle)
            model.setInPlatoon(vehicleState == Vehicle.VEHICLE_STATE.IN_PREBATTLE)
            model.setLevel(self.__portalController.getCurrentVehicleLevel(vehicle))
            model.setHasUpdate(self.__portalController.canUpgradeVehicle(vehicle))
            model.setVehicleType(vehicle.type)
            array.addViewModel(model)

        array.invalidate()

    def _fillPortalQuestWidget(self, model):
        model.setCurrent(self.__portalController.getFinishedLevelsCount())
        model.setMax(self.__portalController.getTotalLevelsCount())

    def __onProgressionClicked(self):
        showPortalProgressionView()

    def __onComplexityChange(self, args):
        self.__portalController.battleLevel = int(args['intCD'])
        self._updateModel()

    def __onVehicleSelect(self, args):
        vehID = int(args['id'])
        self.__portalController.setCurrentSelectedVehicle(vehID)
        selectedVehicle = self.__portalController.getCurrentSelectedVehicle()
        if not selectedVehicle:
            g_currentVehicle.selectNoVehicle()
        else:
            g_currentVehicle.selectVehicle(selectedVehicle.invID)
        self._updateModel()

    def __onShowSettings(self, *args, **kwArgs):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), EVENT_BUS_SCOPE.LOBBY)

    def __onClose(self, *args, **kwArgs):
        self.destroyWindow()
        self.__portalController.selectRandomBattle()

    def __onAboutEvent(self, *args, **kwArgs):
        showPortalInfoPage()

    def __onShopClicked(self, *args, **kwArgs):
        showShop(getShopPageURL())

    def __onUpgradeVehicleClicked(self):
        showPortalUpgradeView()

    def __onClientUpdated(self, diff, _):
        self._updateModel()

    def _getEvents(self):
        return ((self.viewModel.onProgressionClicked, self.__onProgressionClicked),
         (self.viewModel.onVehicleSelect, self.__onVehicleSelect),
         (self.viewModel.onComplexityChange, self.__onComplexityChange),
         (self.viewModel.onStartMoving, self.__onStartMoving),
         (self.viewModel.onMoveSpace, self.__onMoveSpace),
         (self.viewModel.onAboutEvent, self.__onAboutEvent),
         (self.viewModel.onShowSettings, self.__onShowSettings),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onShopClicked, self.__onShopClicked),
         (self.viewModel.onUpgradeVehicle, self.__onUpgradeVehicleClicked),
         (g_playerEvents.onClientUpdated, self.__onClientUpdated),
         (self.__portalController.onMaxAvailableComplexityLevelChanged, self.__onMaxAvailableComplexityLevelChanged),
         (self.__portalController.onPortalSquadStateChanged, self.__onPortalSquadStateChanged))

    def __onStartMoving(self):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': True}), EVENT_BUS_SCOPE.GLOBAL)

    def __onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')}), EVENT_BUS_SCOPE.GLOBAL)
            return

    def __onMaxAvailableComplexityLevelChanged(self):
        with self.viewModel.transaction() as model:
            self._fillComplexityLevels(model.complexityLevelWidget.levels)

    def __onPortalSquadStateChanged(self, isInSquad, isCommander):
        isLevelsWidgetEnabled = not isInSquad or isCommander
        with self.viewModel.transaction() as model:
            model.complexityLevelWidget.setIsEnabled(isLevelsWidgetEnabled)

    def __updateSquadState(self):
        prbDispatcher = self.__portalController.prbDispatcher
        if prbDispatcher is not None:
            isInSquad = prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.PORTAL)
            if isInSquad:
                entity = prbDispatcher.getEntity()
                isCommander = entity.isCommander()
                self.__onPortalSquadStateChanged(isInSquad, isCommander)
        return

    def updateVisibilityHangarHeaderMenu(self, isVisible=False):
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING if not isVisible else HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
