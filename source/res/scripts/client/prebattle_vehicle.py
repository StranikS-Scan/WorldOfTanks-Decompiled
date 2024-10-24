# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/prebattle_vehicle.py
import logging
import random
import CGF
from ClientSelectableCameraObject import ClientSelectableCameraObject
from Event import Event
from account_helpers import AccountSettings
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from account_helpers.AccountSettings import EVENT_VEHICLE, EVENT_SAVED_VEHICLE
from EventVehicle import EventVehicle
from HangarVehicle import HangarVehicle
from gui.vehicle_view_states import createState4CurrentVehicle
from gui.wt_event.wt_event_helpers import g_execute_after_all_event_vehicles_loaded
from helpers import dependency
from constants import PREBATTLE_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from shared_utils import first, nextTick
from skeletons.prebattle_vehicle import IPrebattleVehicle
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from gui.prb_control import prbDispatcherProperty
from skeletons.gui.game_control import IWhiteTigerController
_logger = logging.getLogger(__name__)

class PrebattleVehicle(IPrebattleVehicle):
    itemsCache = dependency.descriptor(IItemsCache)
    hangarSpace = dependency.descriptor(IHangarSpace)
    __wtController = dependency.descriptor(IWhiteTigerController)

    def __init__(self):
        super(PrebattleVehicle, self).__init__()
        self.onChanged = Event()

    def fini(self):
        self.onChanged.clear()

    @g_execute_after_all_event_vehicles_loaded
    def switchCamera(self, vehicle):
        ClientSelectableCameraObject.switchCamera(vehicle)

    def select(self, vehicle):
        isEvent = self.__wtController.isEventPrbActive()
        if vehicle is None or vehicle == self.item or not isEvent:
            return
        else:
            eventType = first(vehicle.tags & VEHICLE_TAGS.WT_VEHICLES)
            if not eventType:
                _logger.error('This service is only suitable for event vehicles')
                return
            AccountSettings.setFavorites(EVENT_VEHICLE, vehicle.invID)
            query = CGF.Query(self.hangarSpace.spaceID, EventVehicle)
            if not query.empty():
                for ev in query.values():
                    if ev.eventType == eventType:
                        ev.select(vehicle.descriptor)

                nextTick(self.onChanged)()
            else:
                self.__selectDefer(eventType, vehicle)
            return

    @g_execute_after_all_event_vehicles_loaded
    def __selectDefer(self, eventType, vehicle):

        def select():
            query = CGF.Query(self.hangarSpace.spaceID, EventVehicle)
            for ev in query.values():
                if ev.eventType == eventType:
                    ev.select(vehicle.descriptor)

            nextTick(self.onChanged)()

        nextTick(select)()

    def selectVehicle(self, invID):
        vehicle = self.itemsCache.items.getVehicle(invID)
        if not vehicle or not vehicle.isHunterOrBoss:
            self.selectAny()
        else:
            self.select(vehicle)

    def selectPreviousVehicle(self):
        self.selectVehicle(self.lastInvID)

    def selectAny(self):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.HangarSimpleEvent.UPDATE_CAROUSEL_VEHICLE_STATES), scope=EVENT_BUS_SCOPE.LOBBY)
        bosses = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS({VEHICLE_TAGS.EVENT_BOSS}))
        hunters = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS({VEHICLE_TAGS.EVENT_HUNTER}))
        vehicle = self.__getSavedEventVehicle()
        if vehicle:
            self.select(vehicle)
            return
        vehicle = self.itemsCache.items.getVehicle(self.lastInvID)
        if not self.isSquad():
            for boss in bosses.itervalues():
                if boss.isSpecialBoss:
                    vehicle = boss
                if self.__wtController.hasEnoughTickets():
                    vehicle = boss

        if not vehicle or not vehicle.isHunterOrBoss:
            vehicle = random.choice(hunters.values())
        elif vehicle.isBoss:
            isAnyBossAvailable = self.__wtController.hasEnoughTickets() or self.__wtController.hasSpecialBoss()
            if self.isSquad() or not isAnyBossAvailable:
                vehicle = random.choice(hunters.values())
        self.select(vehicle)

    def selectNone(self):
        query = CGF.Query(self.hangarSpace.spaceID, HangarVehicle)
        if query.empty():
            _logger.error('Failed to select HangerVehicle. Reason: HangarVehicle is missing.')
        else:
            vehicle = first(query.values())
            self.switchCamera(vehicle)

    def getViewState(self):
        return createState4CurrentVehicle(self)

    def isPresent(self):
        return self.item is not None

    def isPremiumIGR(self):
        return self.isPresent() and self.item.isPremiumIGR

    def isInHangar(self):
        return self.isPresent() and not self.item.isInBattle

    def isDisabled(self):
        return self.isPresent() and self.item.isDisabled

    def isBroken(self):
        return self.isPresent() and self.item.isBroken

    def isDisabledInRent(self):
        return self.isPresent() and self.item.rentalIsOver

    def isOnlyForEventBattles(self):
        return self.isPresent() and self.item.isOnlyForEventBattles

    def isOutfitLocked(self):
        return self.isPresent() and self.item.isOutfitLocked

    def isCustomizationEnabled(self):
        return not self.isPresent() or self.item.isCustomizationEnabled()

    def isSquad(self):
        if self.prbDispatcher:
            state = self.prbDispatcher.getFunctionalState()
            isSquad = state.isInUnit(PREBATTLE_TYPE.SQUAD) or state.isInUnit(PREBATTLE_TYPE.WHITE_TIGER) or state.isInUnit(PREBATTLE_TYPE.EPIC)
            return isSquad
        return False

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @property
    def item(self):
        query = CGF.Query(self.hangarSpace.spaceID, EventVehicle)
        if query.empty() or not query.values():
            return None
        else:
            for ev in query.values():
                if ev.state == CameraMovementStates.ON_OBJECT:
                    return self.itemsCache.items.getItemByCD(ev.typeDescriptor.type.compactDescr)

            return None

    @property
    def invID(self):
        return 0 if self.item is None else self.item.invID

    @property
    def lastInvID(self):
        return AccountSettings.getFavorites(EVENT_VEHICLE)

    def __getSavedEventVehicle(self):
        invID = AccountSettings.getFavorites(EVENT_SAVED_VEHICLE) or 0
        AccountSettings.setFavorites(EVENT_SAVED_VEHICLE, None)
        vehicle = self.itemsCache.items.getVehicle(invID)
        if not vehicle or not vehicle.isHunterOrBoss:
            return
        else:
            isVehicleSuitable = vehicle.isBoss and self.__wtController.hasEnoughTickets() or vehicle.isSpecialBoss and self.__wtController.hasSpecialBoss() or not vehicle.isBoss
            return vehicle if isVehicleSuitable else None
