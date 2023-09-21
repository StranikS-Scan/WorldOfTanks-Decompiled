# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EventVehicle.py
import logging
import GenericComponents
import CGF
import Projectiles
from ClientSelectableCameraObject import ClientSelectableCameraObject
from aih_constants import CTRL_MODES, CTRL_MODE_NAME
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from EventPortal import EventPortal
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from items.components.c11n_constants import SeasonType
from shared_utils import findFirst
from skeletons.prebattle_vehicle import IPrebattleVehicle
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.shared import IItemsCache
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
_logger = logging.getLogger(__name__)

class _EventVehicleAppearance(HangarVehicleAppearance):

    def _getActiveOutfit(self, vDesc):
        vehicle = self.itemsCache.items.getItemByCD(vDesc.type.compactDescr)
        outfit = vehicle.getOutfit(SeasonType.SUMMER)
        if not outfit:
            vehicleCD = vehicle.descriptor.makeCompactDescr()
            outfit = self.customizationService.getEmptyOutfitWithNationalEmblems(vehicleCD=vehicleCD)
        return outfit


class _EventBossAppearance(_EventVehicleAppearance):
    __gameEventCtrl = dependency.descriptor(IEventBattlesController)

    def __init__(self, spaceID, vehicle):
        super(_EventBossAppearance, self).__init__(spaceID, vehicle)
        self.__gameEventCtrl.onTicketsUpdate += self.__updateTickets
        self.loadState.subscribe(self.__onLoad, self.__onUnload)

    def destroy(self):
        self.__gameEventCtrl.onTicketsUpdate -= self.__updateTickets
        self.loadState.unsubscribe(self.__onLoad, self.__onUnload)
        super(_EventBossAppearance, self).destroy()

    def __onLoad(self):
        if self.findComponentByType(Projectiles.GunReloadedComponent) is None:
            self.createComponent(Projectiles.GunReloadedComponent)
        self.__updateTickets()
        return

    def __onUnload(self):
        pass

    def __updateTickets(self):
        isSpecial = False
        descriptor = self.typeDescriptor
        if descriptor is not None:
            isSpecial = VEHICLE_TAGS.EVENT_SPECIAL_BOSS in descriptor.type.tags
        hasTickets = bool(self.__gameEventCtrl.getTicketCount()) or isSpecial
        self.removeComponentByType(GenericComponents.ControlModeStatus)
        if hasTickets:
            self.createComponent(GenericComponents.ControlModeStatus, CTRL_MODES.index(CTRL_MODE_NAME.ARCADE))
        else:
            self.createComponent(GenericComponents.ControlModeStatus, CTRL_MODES.index(CTRL_MODE_NAME.SNIPER))
        return


class EventVehicle(ClientSelectableCameraVehicle):
    _itemsCache = dependency.descriptor(IItemsCache)
    _prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    _gameEventCtrl = dependency.descriptor(IEventBattlesController)

    def select(self, descriptor):
        if not self.typeDescriptor or descriptor.type.id != self.typeDescriptor.type.id:
            self.recreateVehicle(descriptor)
        if self.model:
            self._gameEventCtrl.getSelectedVehicleSoundMgr().playSound(self.model.root, descriptor.name)
        if self.eventType == VEHICLE_TAGS.EVENT_HUNTER:
            ClientSelectableCameraObject.switchCamera(self, 'EventTankHunter')
        else:
            ClientSelectableCameraObject.switchCamera(self, 'EventTankBoss')
        portal = self._getPortalEntity()
        if portal is not None:
            portal.setEnable(False)
        return

    def onEnterWorld(self, prereqs):
        super(EventVehicle, self).onEnterWorld(prereqs)
        self._itemsCache.onSyncCompleted += self.__onCacheResync
        descriptor = self._chooseVehicle()
        self.recreateVehicle(descriptor)
        self.entityGameObject.createComponent(GenericComponents.BattleStage, 1, 1)

    def onLeaveWorld(self):
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        self.setEnable(False)
        if self.typeDescriptor:
            self._gameEventCtrl.getSelectedVehicleSoundMgr().stopSound(self.typeDescriptor.name)
        super(EventVehicle, self).onLeaveWorld()

    def onMouseClick(self):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.HangarSimpleEvent.EVENT_VEHICLE_SELECTED), scope=EVENT_BUS_SCOPE.LOBBY)
        if not self._isPortalSelected():
            portal = self._getPortalEntity()
            if portal is not None:
                if not portal.isMouseSelectionLocked:
                    self._gameEventCtrl.doSelectEventPrb()
                else:
                    _logger.info("Click operation for vehicle is forbidden due to portal's cooldown!")
                    return False
        vehicle = self._itemsCache.items.getItemByCD(self.typeDescriptor.type.compactDescr)
        self._prebattleVehicle.select(vehicle)
        return True

    def onDeselect(self):
        portal = self._getPortalEntity()
        if portal is not None:
            portal.setEnable(True)
        super(EventVehicle, self).onDeselect()
        return

    def setHighlight(self, show, fallback=False):
        super(EventVehicle, self).setHighlight(show)
        if fallback:
            return
        else:
            portal = self._getPortalEntity()
            if portal is not None:
                portal.setHighlight(show, fallback=True)
            for vehicle in self._getEventVehicles():
                if vehicle is not self:
                    vehicle.setHighlight(show, fallback=True)

            return

    def _isPortalSelected(self):
        portalEntity = self._getPortalEntity()
        return not portalEntity.enabled if portalEntity is not None else False

    def _getPortalEntity(self):
        query = CGF.Query(self.spaceID, EventPortal)
        return query.values()[0] if not query.empty() else None

    def _getEventVehicles(self):
        otherVehicles = []
        query = CGF.Query(self.spaceID, EventVehicle)
        if not query.empty():
            for vehicle in query.values():
                otherVehicles.append(vehicle)

        return otherVehicles

    def _chooseVehicle(self):
        vehicle = None
        if self.eventType == VEHICLE_TAGS.EVENT_BOSS:
            vehicles = self._itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.EVENT_SPECIAL_BOSS]))
            if vehicles:
                vehicle = vehicles.values()[0]
                return vehicle.descriptor
        if self.eventType == VEHICLE_TAGS.EVENT_HUNTER:
            pass
        vehicles = self._itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.HAS_TAGS([self.eventType]) | REQ_CRITERIA.INVENTORY)
        if vehicles:
            if self.eventType == VEHICLE_TAGS.EVENT_BOSS:
                vehicle = findFirst(lambda veh: VEHICLE_TAGS.EVENT_SPECIAL_BOSS in veh.tags, vehicles.values(), vehicles.values()[0])
            elif self.eventType == VEHICLE_TAGS.EVENT_HUNTER:
                lastInvID = self._prebattleVehicle.lastInvID
                vehicle = findFirst(lambda veh: veh.invID == lastInvID, vehicles.values(), vehicles.values()[0])
            if vehicle is not None:
                return vehicle.descriptor
        return

    def _createAppearance(self):
        return _EventBossAppearance(self.spaceID, self) if self.eventType == VEHICLE_TAGS.EVENT_BOSS else _EventVehicleAppearance(self.spaceID, self)

    def __onCacheResync(self, _, __):
        if not self.typeDescriptor:
            descriptor = self._chooseVehicle()
            self.recreateVehicle(descriptor)
