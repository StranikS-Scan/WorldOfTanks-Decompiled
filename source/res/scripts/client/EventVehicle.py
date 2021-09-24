# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EventVehicle.py
import logging
import ArenaComponents
import CGF
import Projectiles
from cgf_components import IsSelected, IsHighlighted
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from EventPortal import EventPortal
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from items.components.c11n_constants import SeasonType
from shared_utils import findFirst
from skeletons.prebattle_vehicle import IPrebattleVehicle
from skeletons.gui.game_control import IGameEventController
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
    __gameEventCtrl = dependency.descriptor(IGameEventController)

    def __init__(self, spaceID, vehicle):
        super(_EventBossAppearance, self).__init__(spaceID, vehicle)
        self.__gameEventCtrl.onTicketsUpdate += self.__updateTickets

    def destroy(self):
        self.__gameEventCtrl.onTicketsUpdate -= self.__updateTickets
        super(_EventBossAppearance, self).destroy()

    def _onOutfitReady(self):
        super(_EventBossAppearance, self)._onOutfitReady()
        if self.findComponentByType(Projectiles.GunReloadedComponent) is None:
            self.createComponent(Projectiles.GunReloadedComponent)
        self.__updateTickets()
        return

    def __updateTickets(self):
        isSpecial = False
        descriptor = self.typeDescriptor
        if descriptor is not None:
            isSpecial = VEHICLE_TAGS.EVENT_SPECIAL_BOSS in descriptor.type.tags
        hasTickets = bool(self.__gameEventCtrl.getTicketCount()) or isSpecial
        if hasTickets:
            self.removeComponentByType(ArenaComponents.TriggerComponent)
        elif self.findComponentByType(ArenaComponents.TriggerComponent) is None:
            self.createComponent(ArenaComponents.TriggerComponent, 'sniper')
        return


class EventVehicle(ClientSelectableCameraVehicle):
    _itemsCache = dependency.descriptor(IItemsCache)
    _prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    _gameEventCtrl = dependency.descriptor(IGameEventController)

    def select(self, descriptor):
        if self.entityGameObject.findComponentByType(IsSelected) is None:
            query = CGF.Query(self.hangarSpace.spaceID, (EventVehicle, IsSelected))
            for eventVehicle, _ in query.values():
                eventVehicle.deselect()

            self.entityGameObject.createComponent(IsSelected)
        if not self.typeDescriptor or descriptor.type.id != self.typeDescriptor.type.id:
            self.recreateVehicle(descriptor)
        if self.model:
            self._gameEventCtrl.getSelectedVehicleSoundMgr().playSound(self.model.root, descriptor.name)
        return

    def deselect(self):
        self.entityGameObject.removeComponentByType(IsSelected)

    def onEnterWorld(self, prereqs):
        super(EventVehicle, self).onEnterWorld(prereqs)
        descriptor = self._chooseVehicle()
        self.recreateVehicle(descriptor)
        self.entityGameObject.createComponent(ArenaComponents.BattleStage, 1, 1)

    def onLeaveWorld(self):
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
                    return True
                _logger.info("Click operation for vehicle is forbidden due to portal's cooldown!")
                return False
        vehicle = self._itemsCache.items.getItemByCD(self.typeDescriptor.type.compactDescr)
        self._prebattleVehicle.select(vehicle)
        return True

    def onDeselect(self, newSelectedObject):
        self._gameEventCtrl.getSelectedVehicleSoundMgr().stopSound(self.typeDescriptor.name)
        self.entityGameObject.removeComponentByType(IsSelected)
        super(EventVehicle, self).onDeselect(newSelectedObject)

    def setHighlight(self, show, fallback=False):
        if fallback:
            return super(EventVehicle, self).setHighlight(show)
        else:
            portal = self._getPortalEntity()
            if portal is not None and not self._isPortalSelected():
                self._highlightEntity(portal, show)
                return
            self._highlightEntity(self, show)
            return

    def _highlightEntity(self, entity, value):
        if value:
            if entity.entityGameObject.findComponentByType(IsHighlighted) is not None:
                return
            entity.entityGameObject.createComponent(IsHighlighted)
        else:
            entity.entityGameObject.removeComponentByType(IsHighlighted)
        return

    def _isPortalSelected(self):
        portalEntity = self._getPortalEntity()
        return portalEntity.entityGameObject.findComponentByType(IsSelected) is not None if portalEntity is not None else False

    def _getPortalEntity(self):
        query = CGF.Query(self.spaceID, EventPortal)
        return query.values()[0] if not query.empty() else None

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
