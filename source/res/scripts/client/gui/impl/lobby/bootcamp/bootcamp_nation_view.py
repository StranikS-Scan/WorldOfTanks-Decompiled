# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bootcamp/bootcamp_nation_view.py
from PlatoonTank import PlatoonTankInfo
from bootcamp.Bootcamp import g_bootcamp, BOOTCAMP_SOUND
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.bootcamp.bootcamp_nation_model import BootcampNationModel
from gui.impl.gen.view_models.views.bootcamp.bootcamp_nation_view_model import BootcampNationViewModel
from gui.impl.gen.view_models.views.bootcamp.preview_model import PreviewModel
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.gui_items.Vehicle import getIconResourceName
from helpers import dependency
from items import vehicles
from nations import INDICES as NATIONS_INDICES, MAP as NATIONS_MAP
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from tutorial.gui.Scaleform.pop_ups import TutorialWulfWindowView
from uilogging.deprecated.bootcamp.constants import BC_LOG_KEYS
from uilogging.deprecated.bootcamp.loggers import BootcampLogger

class BootcampNationView(TutorialWulfWindowView):
    __slots__ = ('__nationsOrder', '__promoNationsOrder', '__isPromote', '__vehicleSecondName', '__loadingTanksNum')
    uiBootcampLogger = BootcampLogger(BC_LOG_KEYS.BC_NATION_SELECT)
    platoonController = dependency.descriptor(IPlatoonController)
    hangarSpace = dependency.descriptor(IHangarSpace)
    itemsCache = dependency.descriptor(IItemsCache)
    FIRST_SLOT = 0
    SECOND_SLOT = 1
    THIRD_SLOT = 2
    BUTTON_HINT_EFFECT = 'BootcampNationSelectButton'
    NATIONS_HINT_EFFECT = 'BootcampNationMainNations'

    def __init__(self):
        super(BootcampNationView, self).__init__()
        self.__nationsOrder = None
        self.__promoNationsOrder = None
        self.__isPromote = False
        self.__vehicleSecondName = None
        self.__loadingTanksNum = 0
        return

    @property
    def viewModel(self):
        return super(BootcampNationView, self).getViewModel()

    def getLayoutID(self):
        return R.views.lobby.bootcamp.BootcampNationView()

    def _createModel(self):
        return BootcampNationViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BootcampNationView, self)._onLoading(*args, **kwargs)
        g_eventBus.addListener(events.TutorialEvent.ON_COMPONENT_FOUND, self.__onItemFound, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, self.__onPlatoonTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.hangarSpace.onVehicleChanged += self.__onVehicleChanged
        self.__nationsOrder, self.__promoNationsOrder = g_bootcamp.getNationsOrder('unlocked', 'locked')
        with self.viewModel.transaction() as model:
            self._fillNationsList(model.getNationsList(), self.__nationsOrder, False)
            self._fillNationsList(model.getPromoteNationsList(), self.__promoNationsOrder, True)
            model.onNationSelected += self.__onNationSelected
            model.onNationShow += self.__onNationShow
            model.onMoveSpace += self.__onMoveSpace
            model.onEscPressed += self.__onEscPressed
            self.__updateSelectedNation(model, NATIONS_MAP[g_bootcamp.nation], False)

    def _fillNationsList(self, nationsListModel, nationsOrder, isPromote):
        for nationId in nationsOrder:
            nationModel = BootcampNationModel()
            nationModel.setId(nationId)
            nationModel.setIcon(R.images.gui.maps.icons.bootcamp.rewards.dyn('nationsSelect_{}'.format(nationId))())
            if isPromote:
                nationModel.setLabel(backport.text(R.strings.bootcamp.award.options.nation.dyn(nationId)()))
            else:
                nationData = g_bootcamp.getNationData(NATIONS_INDICES[nationId])
                vehicle = self.itemsCache.items.getVehicles()[nationData['vehicle_first']]
                nationModel.setVehicleIcon(R.images.gui.maps.icons.vehicle.dyn(getIconResourceName(vehicle.name))())
                nationModel.setLabel(vehicle.descriptor.type.shortUserString)
            nationsListModel.addViewModel(nationModel)

    def _finalize(self):
        self.viewModel.onNationSelected -= self.__onNationSelected
        self.viewModel.onNationShow -= self.__onNationShow
        self.viewModel.onMoveSpace -= self.__onMoveSpace
        self.viewModel.onEscPressed -= self.__onEscPressed
        g_eventBus.removeListener(events.TutorialEvent.ON_COMPONENT_FOUND, self.__onItemFound, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, self.__onPlatoonTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.hangarSpace.onVehicleChanged -= self.__onVehicleChanged
        super(BootcampNationView, self)._finalize()

    def __onItemFound(self, event):
        if event.targetID in (self.BUTTON_HINT_EFFECT, self.NATIONS_HINT_EFFECT):
            self._showHint(event.targetID)
            self.soundManager.playSound(BOOTCAMP_SOUND.NEW_UI_ELEMENT_SOUND)

    def __onNationSelected(self, args):
        nationId = args.get('id')
        self.uiBootcampLogger.log(nationId)
        self.setResultVar(NATIONS_INDICES[nationId])
        self.submit()

    def __onNationShow(self, args):
        nationId = args.get('id')
        isPromote = args.get('isPromote')
        with self.viewModel.transaction() as model:
            self.__updateSelectedNation(model, nationId, isPromote)

    def __updateSelectedNation(self, model, nationId, isPromote):
        self.__isPromote = isPromote
        model.setIsPromote(self.__isPromote)
        model.setSelectedNation(self.__promoNationsOrder.index(nationId) if self.__isPromote else self.__nationsOrder.index(nationId))
        self.__clearPlatoonTanks()
        nationData = g_bootcamp.getNationData(NATIONS_INDICES[nationId])
        if self.__isPromote:
            model.setSelectedTitle(backport.text(R.strings.bootcamp.preview.dyn(nationId).title()))
            previewVehiclesList = model.getPreviewVehiclesList()
            previewVehiclesList.clear()
            platoonTanks = dict()
            for index, vehicleId in enumerate(nationData['preview_vehicles']):
                sectionName = 'preview_vehicle_{}'.format(index + 1)
                vehicleDescr = vehicles.VehicleDescr(typeName=vehicleId)
                vehicleModel = PreviewModel()
                vehicleModel.setName(vehicleDescr.type.userString)
                vehicleModel.setDescription(R.strings.bootcamp.preview.dyn(nationId).dyn(sectionName)())
                previewVehiclesList.addViewModel(vehicleModel)
                if index == self.SECOND_SLOT:
                    vehicle = self.itemsCache.items.getVehicles()[vehicleDescr.type.compactDescr]
                    g_bootcamp.installModules(nationData, sectionName, vehicle.descriptor)
                    self.hangarSpace.startToUpdateVehicle(vehicle)
                    self.__vehicleSecondName = vehicleDescr.type.userString
                g_bootcamp.installModules(nationData, sectionName, vehicleDescr)
                platoonTanks[index] = PlatoonTankInfo(True, vehicleDescr.makeCompactDescr(), '', None, 0, 0, vehicleDescr.type.userString)

            self.__loadingTanksNum = len(platoonTanks)
            Waiting.show('updateVehicle')
            model.setIsPreviewLoading(True)
            self.platoonController.onPlatoonTankUpdated(platoonTanks)
            space = self.hangarSpace.space
            if space is not None:
                cameraManager = space.getCameraManager()
                cameraManager.setPlatoonStartingCameraPosition()
        else:
            vehicleDescr = vehicles.VehicleDescr(typeName=nationData['vehicle_first_descr'])
            model.setSelectedTitle(vehicleDescr.type.shortUserString)
            model.setSelectedDescription(R.strings.bootcamp.award.options.description.dyn(nationId)())
            self.__updateSecondVehicleMarker(False)
            g_bootcamp.previewNation(NATIONS_INDICES[nationId])
        return

    def __onVehicleChanged(self):
        if self.__isPromote:
            self.__updateSecondVehicleMarker(True)

    def __onPlatoonTankLoaded(self, _):
        self.__loadingTanksNum -= 1
        if self.__loadingTanksNum <= 0:
            self.viewModel.setIsPreviewLoading(False)
            Waiting.hide('updateVehicle')

    def __clearPlatoonTanks(self):
        self.platoonController.onPlatoonTankRemove(self.FIRST_SLOT)
        self.platoonController.onPlatoonTankRemove(self.THIRD_SLOT)

    @staticmethod
    def __onMoveSpace(args=None):
        if args is None:
            return
        else:
            ctx = {'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')}
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx=ctx), EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx=ctx), EVENT_BUS_SCOPE.GLOBAL)
            return

    @staticmethod
    def __onEscPressed():
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateSecondVehicleMarker(self, isVisible):
        entity = self.hangarSpace.getVehicleEntity()
        if entity is None or entity.model is None:
            return
        else:
            g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.BOOTCAMP_SECOND_TANK_MARKER, ctx={'entity': entity,
             'playerName': self.__vehicleSecondName,
             'isVisible': isVisible}), scope=EVENT_BUS_SCOPE.LOBBY)
            return
