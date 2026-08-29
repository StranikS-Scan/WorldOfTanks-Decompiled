# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EventVehicle.py
import math
import logging
import GenericComponents
import CGF
import Projectiles
from ClientSelectableCameraObject import ClientSelectableCameraObject
from aih_constants import CTRL_MODES, CTRL_MODE_NAME
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from EventPortal import EventPortal
from helpers import dependency
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from items.components.c11n_constants import SeasonType
from skeletons.prebattle_vehicle import IPrebattleVehicle
from skeletons.gui.game_control import IWhiteTigerController
from skeletons.gui.shared import IItemsCache
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from vehicle_systems import model_assembler
from wt_settings import g_wt_config
from skeletons.helpers.statistics import IStatisticsCollector
from helpers.statistics import HANGAR_LOADING_STATE
from PlayerEvents import g_playerEvents
from gui.game_loading.resources.consts import Milestones
from gui.wt_event.wt_event_helpers import g_execute_after_all_event_vehicles_loaded
_logger = logging.getLogger(__name__)

class _EventVehicleAppearance(HangarVehicleAppearance):

    def __init__(self, spaceId, vEntity, turretYaw=0.0, gunPitch=0.0):
        super(_EventVehicleAppearance, self).__init__(spaceId, vEntity)
        self.__turretYaw = turretYaw
        self.__gunPitch = gunPitch

    def _getActiveOutfit(self, vDesc):
        vehicle = self.itemsCache.items.getItemByCD(vDesc.type.compactDescr)
        outfit = vehicle.getOutfit(SeasonType.SUMMER)
        if not outfit:
            vehicleCD = vehicle.descriptor.makeCompactDescr()
            outfit = self.customizationService.getEmptyOutfitWithNationalEmblems(vehicleCD=vehicleCD)
        return outfit

    def _getTurretYaw(self):
        return self.__turretYaw

    def _getGunPitch(self):
        return self.__gunPitch


class _EventBossAppearance(_EventVehicleAppearance):

    def __init__(self, spaceID, vehicle, turretYaw=0.0, gunPitch=0.0):
        super(_EventBossAppearance, self).__init__(spaceID, vehicle, turretYaw, gunPitch)
        g_wt_config.onBossTokenUpdate += self.__onBossTokenUpdate
        g_wt_config.onEventTokenUpdate += self.__onBossTokenUpdate
        self.loadState.subscribe(self.__onLoad, self.__onUnload)

    def destroy(self):
        g_wt_config.onBossTokenUpdate -= self.__onBossTokenUpdate
        g_wt_config.onEventTokenUpdate -= self.__onBossTokenUpdate
        self.loadState.unsubscribe(self.__onLoad, self.__onUnload)
        super(_EventBossAppearance, self).destroy()

    def __onLoad(self):
        if self.findComponentByType(Projectiles.GunReloadedComponent) is None:
            self.createComponent(Projectiles.GunReloadedComponent)
        self.__onBossTokenUpdate(None, None)
        return

    def __onUnload(self):
        pass

    def _onOutfitReady(self):
        model_assembler.assembleCustomLogicComponents(self, self.typeDescriptor, self.attachments, self.modelAnimators)

    def _applyGunAndTurretDir(self):
        return True

    def __onBossTokenUpdate(self, _, __):
        hasTickets = g_wt_config.hasTokensForBattle(self.typeDescriptor.type.compactDescr)
        self.removeComponentByType(GenericComponents.ControlModeStatus)
        if hasTickets:
            self.createComponent(GenericComponents.ControlModeStatus, CTRL_MODES.index(CTRL_MODE_NAME.ARCADE))
        else:
            self.createComponent(GenericComponents.ControlModeStatus, CTRL_MODES.index(CTRL_MODE_NAME.SNIPER))


class EventVehicle(ClientSelectableCameraVehicle):
    _itemsCache = dependency.descriptor(IItemsCache)
    _prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    _gameEventCtrl = dependency.descriptor(IWhiteTigerController)
    _statsCollector = dependency.descriptor(IStatisticsCollector)

    def select(self, descriptor):
        if not self.typeDescriptor or descriptor.type.id != self.typeDescriptor.type.id:
            self.recreateVehicle(descriptor)
        if self.model:
            self._gameEventCtrl.getSelectedVehicleSoundMgr().playSound(self.model.root, descriptor.name)
        intCD = self.typeDescriptor.type.compactDescr
        vehData = g_wt_config.getVehicleData(intCD)
        ClientSelectableCameraObject.switchCamera(self, vehData.subType)

    def selectForPreview(self, descriptor, outfit):
        if not self.typeDescriptor or descriptor.type.id != self.typeDescriptor.type.id:
            self.recreateVehicle(descriptor, outfit=outfit)
        if self.model:
            self._gameEventCtrl.getSelectedVehicleSoundMgr().playSound(self.model.root, descriptor.name)
        ClientSelectableCameraObject.switchCamera(self, 'hunter')

    def onEnterWorld(self, prereqs):
        super(EventVehicle, self).onEnterWorld(prereqs)
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        g_playerEvents.onLoadingMilestoneReached += self._onLoadingMilestoneReached
        self._statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.START_LOADING_VEHICLE)
        descriptor = self._chooseVehicle()
        self.recreateVehicle(descriptor)

    def onLeaveWorld(self):
        g_playerEvents.onLoadingMilestoneReached -= self._onLoadingMilestoneReached
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        if self.typeDescriptor:
            self._gameEventCtrl.getSelectedVehicleSoundMgr().stopSound(self.typeDescriptor.name)
        super(EventVehicle, self).onLeaveWorld()

    def onMouseClick(self):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.HangarSimpleEvent.EVENT_VEHICLE_SELECTED), scope=EVENT_BUS_SCOPE.LOBBY)
        if not self._isPortalSelected():
            portal = self._getPortalEntity()
            if portal is not None:
                if not portal.isMouseSelectionLocked and self._gameEventCtrl.isAvailable():
                    self._gameEventCtrl.doSelectEventPrb()
                else:
                    _logger.info("Click operation for vehicle is forbidden due to portal's cooldown!")
                    return False
        vehicle = self._itemsCache.items.getItemByCD(self.typeDescriptor.type.compactDescr)
        self._prebattleVehicle.select(vehicle)
        return True

    def _isPortalSelected(self):
        portalEntity = self._getPortalEntity()
        return not portalEntity.enabled if portalEntity is not None else False

    def _getPortalEntity(self):
        query = CGF.Query(self.spaceID, EventPortal)
        return query.values()[0] if not query.empty() and query.values() else None

    def _chooseVehicle(self):
        if self.eventType in ('boss', 'boss_2025'):
            vehicles = g_wt_config.getBossVehiclesData()
            if vehicles:
                for data in vehicles.itervalues():
                    if self.eventType == data.subType:
                        return data.vehicle.descriptor

        if self.eventType == 'hunter':
            intCD = self._gameEventCtrl.accountSettings.savedHunterVehicleCD
            if intCD is None:
                intCD = g_wt_config.getHunterVehiclesData().keys()[0]
            vehicle = g_wt_config.getVehicleData(intCD).vehicle
            return vehicle.descriptor
        else:
            return

    def _createAppearance(self):
        vehicleTurretYaw = math.radians(self.vehicleTurretYaw)
        vehicleGunPitch = math.radians(self.vehicleGunPitch)
        intCD = self.typeDescriptor.type.compactDescr
        return _EventBossAppearance(self.spaceID, self, turretYaw=vehicleTurretYaw, gunPitch=vehicleGunPitch) if g_wt_config.isAnyTypeBoss(intCD) else _EventVehicleAppearance(self.spaceID, self, turretYaw=vehicleTurretYaw, gunPitch=vehicleGunPitch)

    def __onCacheResync(self, _, __):
        if not self.typeDescriptor:
            descriptor = self._chooseVehicle()
            self.recreateVehicle(descriptor)

    @g_execute_after_all_event_vehicles_loaded
    def _onLoadingMilestoneReached(self, milestoneName):
        if milestoneName == Milestones.HANGAR_READY:
            self._statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.FINISH_LOADING_VEHICLE, showSummaryNow=True)
