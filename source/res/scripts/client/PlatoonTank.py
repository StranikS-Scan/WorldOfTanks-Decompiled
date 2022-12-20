# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PlatoonTank.py
import typing
from typing import TYPE_CHECKING
from collections import namedtuple
import logging
import math
import AccountCommands
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from constants import IS_DEVELOPMENT
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IPlatoonController
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import GAME
from vehicle_systems.tankStructure import ModelStates, ColliderTypes
from vehicle_systems import camouflages
from items import vehicles
from items.components.c11n_constants import SeasonType
if TYPE_CHECKING:
    from vehicle_outfit.outfit import Outfit as TOutfit
    from items.vehicles import VehicleDescrType
_logger = logging.getLogger(__name__)
PlatoonTankInfo = namedtuple('PlatoonTankInfo', ('canDisplayModel', 'vehCompDescr', 'vehOutfitCD', 'seasonType', 'marksOnGun', 'clanDBID', 'playerName'))

class _PlatoonTankAppearance(HangarVehicleAppearance):
    _c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, spaceId, vEntity, tankInfo, turretYaw=0.0, gunPitch=0.0):
        super(_PlatoonTankAppearance, self).__init__(spaceId, vEntity)
        self.__tankInfo = tankInfo
        self.__turretYaw = turretYaw
        self.__gunPitch = gunPitch

    def updateTankInfo(self, tankInfo):
        self.__tankInfo = tankInfo

    def _getActiveOutfit(self, vDesc):
        tankInfo = self.__tankInfo
        if tankInfo is None:
            if vDesc:
                vehicleCD = vDesc.makeCompactDescr()
                return self.customizationService.getEmptyOutfitWithNationalEmblems(vehicleCD=vehicleCD)
            return self.itemsFactory.createOutfit()
        else:
            vehCompDescr = tankInfo.vehCompDescr
            if tankInfo.vehOutfitCD:
                if vDesc is None:
                    vDesc = vehicles.VehicleDescr(vehCompDescr)
                outfitComp = camouflages.getOutfitComponent(outfitCD=tankInfo.vehOutfitCD, vehicleDescriptor=vDesc, seasonType=tankInfo.seasonType)
                outfit = self.itemsFactory.createOutfit(component=outfitComp, vehicleCD=vehCompDescr)
                forceHistorical = self.settingsCore.getSetting(GAME.CUSTOMIZATION_DISPLAY_TYPE) < outfit.customizationDisplayType()
                if forceHistorical:
                    outfit = None
            else:
                outfit = None
            if outfit is None:
                outfit = self.customizationService.getEmptyOutfitWithNationalEmblems(vehicleCD=vehCompDescr)
            return outfit

    def _requestClanDBIDForStickers(self, callback):
        callback(AccountCommands.RES_SUCCESS, self.__tankInfo.clanDBID)

    def _getThisVehicleDossierInsigniaRank(self):
        return self.__tankInfo.marksOnGun if self.__tankInfo is not None else 0

    def _getTurretYaw(self):
        return self.__turretYaw

    def _getGunPitch(self):
        return self.__gunPitch

    def _reloadColliderType(self, state):
        pass

    def _getColliderType(self):
        return ColliderTypes.PLATOON_VEHICLE_COLLIDER


class PlatoonTank(ClientSelectableCameraVehicle):
    _platoonCtrl = dependency.descriptor(IPlatoonController)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__tankInfo = None
        ClientSelectableCameraVehicle.__init__(self)
        return

    def onEnterWorld(self, prereqs):
        super(PlatoonTank, self).onEnterWorld(prereqs)
        _logger.debug('Platoon tank with slot index: %s', self.slotIndex)
        self._platoonCtrl.onPlatoonTankUpdated += self._updatePlatoonTank
        self._platoonCtrl.onPlatoonTankVisualizationChanged += self.removeModelFromScene
        self._platoonCtrl.onPlatoonTankRemove += self.__onPlatoonTankRemove
        self._platoonCtrl.registerPlatoonTank(self)
        self.setEnable(False)

    def onLeaveWorld(self):
        self._platoonCtrl.onPlatoonTankUpdated -= self._updatePlatoonTank
        self._platoonCtrl.onPlatoonTankVisualizationChanged -= self.removeModelFromScene
        self._platoonCtrl.onPlatoonTankRemove -= self.__onPlatoonTankRemove
        super(PlatoonTank, self).onLeaveWorld()

    def onMouseClick(self):
        pass

    def removeModelFromScene(self, isEnabled):
        if self.isVehicleLoaded and not isEnabled:
            self._onVehicleDestroy()
            self.__tankInfo = None
            self._isVehicleLoaded = False
        return

    def recreateVehicle(self, typeDescriptor=None, state=ModelStates.UNDAMAGED, callback=None, outfit=None):
        if self.__tankInfo and self.__tankInfo.vehCompDescr != '':
            self.typeDescriptor = vehicles.VehicleDescr(compactDescr=self.__tankInfo.vehCompDescr)
        if self.appearance is not None:
            self.appearance.updateTankInfo(self.__tankInfo)
        super(PlatoonTank, self).recreateVehicle(typeDescriptor, state, callback, outfit)
        return

    if IS_DEVELOPMENT:

        def debugDisplayTankModel(self, tankTypeName):
            if tankTypeName:
                vDescriptor = vehicles.VehicleDescr(typeName=tankTypeName)
                tankInfo = PlatoonTankInfo(True, vDescriptor.makeCompactDescr(), '', SeasonType.SUMMER, 0, 0, vDescriptor.type.userString)
            else:
                tankInfo = PlatoonTankInfo(True, '', '', SeasonType.SUMMER, 0, 0, '')
            self._updatePlatoonTank({self.slotIndex: tankInfo})

    def _createAppearance(self):
        vehicleTurretYaw = math.radians(self.vehicleTurretYaw)
        vehicleGunPitch = math.radians(self.vehicleGunPitch)
        return _PlatoonTankAppearance(self.spaceID, self, self.__tankInfo, turretYaw=vehicleTurretYaw, gunPitch=vehicleGunPitch)

    def _updatePlatoonTank(self, updatedTankInfoDict):
        if self.slotIndex not in updatedTankInfoDict:
            return
        tankInfo = updatedTankInfoDict[self.slotIndex]
        _logger.debug('Updating platoon tank: slot: %s, tankInfo: %s', self.slotIndex, str(tankInfo))
        if tankInfo != self.__tankInfo:
            self.__tankInfo = tankInfo
            if self.__tankInfo and self.__tankInfo.canDisplayModel and self.__tankInfo.vehCompDescr != '':
                _logger.debug('Recreating Vehicle')
                self.recreateVehicle()
            else:
                _logger.debug('Removing Vehicle')
                self.removeModelFromScene(False)

    def _onVehicleLoaded(self):
        super(PlatoonTank, self)._onVehicleLoaded()
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, ctx={'entity': self,
         'playerName': self.__tankInfo.playerName if self.__tankInfo else ''}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onVehicleDestroy(self):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_PLATOON_TANK_DESTROY, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeVehicle()

    def __onPlatoonTankRemove(self, slotIndex):
        if self.slotIndex == slotIndex:
            self.removeModelFromScene(False)

    @staticmethod
    def __getVehicleDescriptorByIntCD(vehicleIntCD):
        _, nationId, itemId = vehicles.parseIntCompactDescr(vehicleIntCD)
        return vehicles.VehicleDescr(typeID=(nationId, itemId))
