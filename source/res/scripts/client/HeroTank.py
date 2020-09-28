# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HeroTank.py
import math
import random
import BigWorld
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import EVENT_VEHICLE
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IHeroTankController
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.game_control import IGameEventController
from skeletons.gui.shared import IItemsCache
from vehicle_systems.tankStructure import ModelStates
from items import vehicles
from constants import IS_DEVELOPMENT
from items.vehicles import makeVehicleTypeCompDescrByName

class _HeroTankAppearance(HangarVehicleAppearance):
    _heroTankCtrl = dependency.descriptor(IHeroTankController)
    _c11nService = dependency.descriptor(ICustomizationService)
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, spaceId, vEntity, turretYaw=0.0, gunPitch=0.0, isBoss=False, isEvent=False):
        super(_HeroTankAppearance, self).__init__(spaceId, vEntity, isEvent)
        self.__season = random.choice(SeasonType.COMMON_SEASONS)
        self.__turretYaw = turretYaw
        self.__gunPitch = gunPitch
        self.__typeDescriptor = vEntity.typeDescriptor
        self.__isBoss = isBoss
        self.__isEvent = isEvent
        self.__hunterStyleID = 990
        self.__bossStyleID = 991
        self.__specialBossStyleID = 992
        self.__isSpecialBoss = False
        self.__vEntity = vEntity

    def _getActiveOutfit(self, vDesc):
        styleId = self._heroTankCtrl.getCurrentTankStyleId()
        vehicleCD = vDesc.makeCompactDescr()
        if self.__isEvent:
            styleId = self.__hunterStyleID
            if self.__isBoss:
                if self.__isSpecialBoss:
                    styleId = self.__specialBossStyleID
                else:
                    styleId = self.__bossStyleID
        if styleId:
            style = self._c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleId)
            return style.getOutfit(self.__season, vehicleCD=vehicleCD)
        return self._c11nService.getEmptyOutfitWithNationalEmblems(vehicleCD)

    def _getTurretYaw(self):
        return self.__turretYaw

    def _getGunPitch(self):
        return self.__gunPitch

    def isSpecialVehicle(self):
        return self.__isSpecialBoss

    def setSpecialVehicle(self, value):
        self.__isSpecialBoss = value


class HeroTank(ClientSelectableCameraVehicle):
    _heroTankCtrl = dependency.descriptor(IHeroTankController)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__heroTankCD = None
        self.wtHunterCD = makeVehicleTypeCompDescrByName('germany:G105_T-55_NVA_DDR_EL')
        self.wtBossCD = makeVehicleTypeCompDescrByName('germany:G98_Waffentrager_E100_TL')
        self.wtSpecialBossCD = makeVehicleTypeCompDescrByName('germany:G98_Waffentrager_E100_TL_S')
        ClientSelectableCameraVehicle.__init__(self)
        return

    def eventSelectedOff(self, event):
        pass

    def fireOnMouseClickEvents(self, vehCD=None):
        if vehCD is None:
            vehCD = self.wtHunterCD
            if self.isBoss:
                vehAppearance = self.getVehicleAppearance()
                if vehAppearance is not None:
                    vehCD = self.wtSpecialBossCD if vehAppearance.isSpecialVehicle() else self.wtBossCD
        if self.isEvent:
            veh = self._itemsCache.items.getItemByCD(vehCD)
            g_currentVehicle.selectVehicle(veh.invID)
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.WT_EVENT_VEHICLED_CLICKED, ctx={'data': {'isEvent': self.isEvent,
                  'vehCD': vehCD}}), EVENT_BUS_SCOPE.LOBBY)
        return

    def registerOnMouseClickEvents(self):
        g_eventBus.addListener(events.HangarVehicleEvent.WT_EVENT_SELECTED, self.__wtEventSelected, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarVehicleEvent.WT_EVENT_SELECTED_OFF, self.__wtEventSelectedOff, EVENT_BUS_SCOPE.LOBBY)

    def unRegisterOnMouseClickEvents(self):
        g_eventBus.removeListener(events.HangarVehicleEvent.WT_EVENT_SELECTED, self.__wtEventSelected, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarVehicleEvent.WT_EVENT_SELECTED_OFF, self.__wtEventSelectedOff, EVENT_BUS_SCOPE.LOBBY)

    def onEnterWorld(self, prereqs):
        super(HeroTank, self).onEnterWorld(prereqs)
        self._hangarSpace.onHeroTankReady += self._updateHeroTank
        self._heroTankCtrl.onUpdated += self._updateHeroTank
        self._heroTankCtrl.onInteractive += self._updateInteractive
        if self.isEvent:
            if not self._gameEventController.isEventPrbActive():
                self.setCollisionsEnable(False)
            g_eventBus.addListener(events.HangarVehicleEvent.WT_EVENT_CAROUSEL_CLICKED, self.__wtEventCarouselClicked, EVENT_BUS_SCOPE.LOBBY)

    def onLeaveWorld(self):
        self._hangarSpace.onHeroTankReady -= self._updateHeroTank
        self._heroTankCtrl.onUpdated -= self._updateHeroTank
        self._heroTankCtrl.onInteractive -= self._updateInteractive
        self.unRegisterOnMouseClickEvents()
        if self.isEvent:
            g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.WT_EVENT_HERO_TANK_LEAVE_WORLD, ctx={'isBoss': self.isBoss}), scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.removeListener(events.HangarVehicleEvent.WT_EVENT_CAROUSEL_CLICKED, self.__wtEventCarouselClicked, EVENT_BUS_SCOPE.LOBBY)
        super(HeroTank, self).onLeaveWorld()

    def __wtEventSelectedOff(self, _):
        if self.isEvent:
            self.setCollisionsEnable(False)
        else:
            self.setEnable(True)

    def __wtEventSelected(self, event):
        if not self.isEvent:
            self.setEnable(False)
            return
        else:
            if self.isEvent:
                self.setCollisionsEnable(True)
            setStoredVehicle = event.ctx.get('data', {}).get('setStoredVehicle', False)
            storedVehicleId = AccountSettings.getFavorites(EVENT_VEHICLE)
            storedVehicleSelected = False
            if setStoredVehicle and storedVehicleId != 0 and not self._gameEventController.isInWTEventSquad():
                storedVehicleSelected = self.__selectStoredVehicle(storedVehicleId)
            if not storedVehicleSelected:
                if self._gameEventController.isInWTEventSquad():
                    if not self.isBoss:
                        self.onMouseClick()
                elif self._gameEventController.hasEnoughTickets() or self._gameEventController.hasSpecialBoss():
                    if self.isBoss:
                        if self._gameEventController.hasSpecialBoss():
                            vehAppearance = self.getVehicleAppearance()
                            if vehAppearance is not None:
                                vehAppearance.setSpecialVehicle(True)
                        self.onMouseClick()
                elif not self.isBoss:
                    self.onMouseClick()
            return

    def onMouseClick(self):
        super(HeroTank, self).onMouseClick()
        if self.isEvent:
            self.setEnable(False)
            self._gameEventController.eventHeroTankIsInFocus = True

    def __wtEventCarouselClicked(self, event):
        data = event.ctx.get('data', None)
        vehCD = data.get('vehCD')
        if vehCD == self.wtHunterCD and not self.isBoss:
            super(HeroTank, self).onMouseClick()
            return
        else:
            vehAppearance = self.getVehicleAppearance()
            if vehAppearance is not None:
                vehAppearance.setSpecialVehicle(vehCD == self.wtSpecialBossCD)
            if self.isBoss and vehCD == self.wtBossCD:
                ClientSelectableCameraVehicle.onMouseClick(self)
                self.fireOnMouseClickEvents(vehCD=self.wtBossCD)
            elif self.isBoss and vehCD == self.wtSpecialBossCD:
                ClientSelectableCameraVehicle.onMouseClick(self)
                self.fireOnMouseClickEvents(vehCD=self.wtSpecialBossCD)
            else:
                return
            super(HeroTank, self).recreateVehicle(None, ModelStates.UNDAMAGED, None)
            self.setCollisionsEnable(True)
            self.setEnable(False)
            return

    def removeModelFromScene(self):
        if self.isVehicleLoaded:
            self._onVehicleDestroy()
            BigWorld.destroyEntity(self.id)

    def recreateVehicle(self, typeDescriptor=None, state=ModelStates.UNDAMAGED, callback=None):
        if self.__isInPreview():
            return
        if self.__heroTankCD and not self.__isInPreview():
            if self.isEvent:
                if self.isBoss:
                    self.typeDescriptor = HeroTank.__getVehicleDescriptorByIntCD(self.wtBossCD)
                else:
                    self.typeDescriptor = HeroTank.__getVehicleDescriptorByIntCD(self.wtHunterCD)
            else:
                self.typeDescriptor = HeroTank.__getVehicleDescriptorByIntCD(self.__heroTankCD)
        super(HeroTank, self).recreateVehicle(typeDescriptor, state, callback)

    def _createAppearance(self):
        vehicleTurretYaw = math.radians(self.vehicleTurretYaw)
        vehicleGunPitch = math.radians(self.vehicleGunPitch)
        return _HeroTankAppearance(self.spaceID, self, turretYaw=vehicleTurretYaw, gunPitch=vehicleGunPitch, isBoss=self.isBoss, isEvent=self.isEvent)

    def _updateHeroTank(self):
        if g_currentPreviewVehicle.item is not None:
            if g_currentPreviewVehicle.item.intCD == self.__heroTankCD:
                return
        self.__heroTankCD = self._heroTankCtrl.getRandomTankCD()
        if self.isEvent:
            self.__heroTankCD = self.wtBossCD if self.isBoss else self.wtHunterCD
        if self.__heroTankCD:
            self.recreateVehicle()
        else:
            self.removeModelFromScene()
        return

    def _updateInteractive(self, interactive):
        if self.enabled != interactive:
            self.setEnable(interactive)
            self._onVehicleDestroy()
            self.recreateVehicle()

    def _onVehicleLoaded(self):
        super(HeroTank, self)._onVehicleLoaded()
        self.registerOnMouseClickEvents()
        if self.enabled:
            g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onVehicleDestroy(self):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __getVehicleDescriptorByIntCD(vehicleIntCD):
        _, nationId, itemId = vehicles.parseIntCompactDescr(vehicleIntCD)
        return vehicles.VehicleDescr(typeID=(nationId, itemId))

    @staticmethod
    def __isInPreview():
        return g_currentPreviewVehicle.item and g_currentPreviewVehicle.isHeroTank

    def __selectStoredVehicle(self, invID):
        storedVehicle = self._itemsCache.items.getVehicle(invID)
        if storedVehicle is not None and storedVehicle.intCD in (self.wtBossCD, self.wtSpecialBossCD):
            if self.isBoss:
                vehAppearance = self.getVehicleAppearance()
                if vehAppearance is not None:
                    vehAppearance.setSpecialVehicle(storedVehicle.intCD == self.wtSpecialBossCD)
                self.onMouseClick()
                if storedVehicle.intCD == self.wtSpecialBossCD:
                    super(HeroTank, self).recreateVehicle(None, ModelStates.UNDAMAGED, None)
            return True
        elif storedVehicle is not None and storedVehicle.intCD == self.wtHunterCD:
            if not self.isBoss:
                self.onMouseClick()
            return True
        else:
            return False


def debugReloadHero(heroName):
    if not IS_DEVELOPMENT:
        return
    for e in BigWorld.entities.values():
        if isinstance(e, HeroTank):
            heroDescriptor = vehicles.VehicleDescr(typeName=heroName)
            e.recreateVehicle(heroDescriptor)
            return
