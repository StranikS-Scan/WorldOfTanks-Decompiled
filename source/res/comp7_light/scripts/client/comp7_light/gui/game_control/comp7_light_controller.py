# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/game_control/comp7_light_controller.py
import typing
import Event
from Event import EventManager
from comp7_light.gui.comp7_light_constants import FUNCTIONAL_FLAG
from comp7_light.helpers.comp7_light_server_settings import Comp7LightServerSettings
from comp7_light.skeletons.gui.game_control import IComp7LightProgressionController
from comp7_light_constants import Configs
from constants import COMP7_LIGHT_SCENE
from gui.game_control.season_provider import SeasonProvider
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, TimerNotifier, SimpleNotifier
from helpers import dependency
from items import vehicles
from skeletons.gui.game_control import IComp7LightController, IHangarSpaceSwitchController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional
    from comp7_light.helpers.comp7_light_server_settings import _Comp7LightConfig
    from gui.shared.gui_items.Vehicle import Vehicle
    from items.artefacts import Equipment

class Comp7LightController(Notifiable, SeasonProvider, IComp7LightController, IGlobalListener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __progressionController = dependency.descriptor(IComp7LightProgressionController)
    __spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)

    def __init__(self):
        super(Comp7LightController, self).__init__()
        self.__comp7LightServerSettings = None
        self.__roleEquipmentsCache = None
        self.__roleOverridesCacheParameterByEquipment = {}
        self.__eventsManager = em = EventManager()
        self.onStatusUpdated = Event.Event(em)
        self.onStatusTick = Event.Event(em)
        self.onModeConfigChanged = Event.Event(em)
        return

    @property
    def isBanned(self):
        return False

    @property
    def isOffline(self):
        return not self.__itemsCache.items.stats.getCacheValue('comp7Light', {}).get('isOnline', True)

    @property
    def battleModifiers(self):
        return self.getModeSettings().battleModifiersDescr

    def init(self):
        super(Comp7LightController, self).init()
        self.addNotificator(SimpleNotifier(self.getTimer, self.__timerUpdate))
        self.addNotificator(TimerNotifier(self.getTimer, self.__timerTick))

    def fini(self):
        self.clearNotification()
        self.__eventsManager.clear()
        self.__clearServerSettings()
        super(Comp7LightController, self).fini()

    def onAccountBecomePlayer(self):
        self.__initServerSettings()
        self.__roleEquipmentsCache = None
        self.__applyRoleEquipmentOverrides()
        return

    def onAccountBecomeNonPlayer(self):
        self.stopNotification()

    def onAvatarBecomePlayer(self):
        if self.__comp7LightServerSettings is None:
            self.__initServerSettings()
        self.__roleEquipmentsCache = None
        self.__applyRoleEquipmentOverrides()
        return

    def onConnected(self):
        self.__spaceSwitchController.onCheckSceneChange += self.__onCheckSceneChange

    def onDisconnected(self):
        self.__clearServerSettings()
        self.__spaceSwitchController.onCheckSceneChange -= self.__onCheckSceneChange
        self.stopNotification()
        self.stopGlobalListening()
        self.__roleEquipmentsCache = None
        return

    def getModeSettings(self):
        return self.__comp7LightServerSettings.comp7LightConfig if self.__comp7LightServerSettings else None

    def isEnabled(self):
        config = self.getModeSettings()
        return config is not None and config.isEnabled

    def isFrozen(self):
        if self.getModeSettings() is not None:
            for primeTime in self.getPrimeTimes().values():
                if primeTime.hasAnyPeriods():
                    return False

        return True

    def hasActiveSeason(self, includePreannounced=False):
        return self.isAvailable() and bool(self.getCurrentSeason())

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen()

    def isBattleModifiersAvailable(self):
        return len(self.battleModifiers) > 0

    def isSuitableVehicle(self, vehicle):
        config = self.getModeSettings()
        if vehicle.level not in config.levels:
            restriction = PRE_QUEUE_RESTRICTION.LIMIT_LEVEL
            ctx = {'levels': config.levels}
        elif vehicle.type in config.forbiddenClassTags:
            restriction = PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_CLASS
            ctx = {'forbiddenClass': vehicle.type}
        elif vehicle.compactDescr in config.forbiddenVehTypes:
            restriction = PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_TYPE
            ctx = {'forbiddenType': vehicle.shortUserName}
        else:
            return None
        return ValidationResult(False, restriction, ctx)

    def hasSuitableVehicles(self):
        criteria = self.__filterEnabledVehiclesCriteria(~REQ_CRITERIA.VEHICLE.EVENT_BATTLE | ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE | REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN)
        v = self.__itemsCache.items.getVehicles(criteria)
        return len(v) > 0

    def isModePrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.COMP7_LIGHT)

    def isProgressionActive(self):
        return self.__progressionController.isEnabled and not self.__progressionController.isFinished

    def vehicleIsAvailableForBuy(self):
        criteria = self.__filterEnabledVehiclesCriteria(REQ_CRITERIA.UNLOCKED)
        criteria |= ~REQ_CRITERIA.VEHICLE.SECRET | ~REQ_CRITERIA.HIDDEN
        vUnlocked = self.__itemsCache.items.getVehicles(criteria)
        return len(vUnlocked) > 0

    def vehicleIsAvailableForRestore(self):
        criteria = self.__filterEnabledVehiclesCriteria(REQ_CRITERIA.VEHICLE.IS_RESTORE_POSSIBLE)
        vRestorePossible = self.__itemsCache.items.getVehicles(criteria)
        return len(vRestorePossible) > 0

    def getPreannouncedSeason(self):
        return None

    def getRoleEquipment(self, roleName):
        return self.__roleEquipments.get(roleName, {}).get('item')

    def getEquipmentStartLevel(self, roleName):
        return self.__roleEquipments.get(roleName, {}).get('startLevel')

    def getRoleEquipmentOverrides(self, roleName):
        return self.__roleEquipments.get(roleName, {}).get('overrides', {})

    def getPoiEquipmentOverrides(self, poiName):
        return self.getModeSettings().poiEquipments.get(poiName, {})

    def getCurrentSeason(self, now=None, includePreannounced=False):
        currentSeason = super(Comp7LightController, self).getCurrentSeason(now=now)
        return currentSeason or (self.getPreannouncedSeason() if includePreannounced else None)

    def __comp7LightCriteria(self, vehicle):
        return self.isSuitableVehicle(vehicle) is None

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onStatusUpdated(status)

    def __timerTick(self):
        self.onStatusTick()

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()

    def __updateProgressionSettings(self):
        config = self.getModeSettings()
        if config is None:
            return
        else:
            self.__progressionController.setSettings(config.progression)
            return

    def __filterEnabledVehiclesCriteria(self, criteria):
        criteria = criteria | REQ_CRITERIA.CUSTOM(self.__comp7LightCriteria)
        return criteria

    def __initServerSettings(self):
        self.__comp7LightServerSettings = Comp7LightServerSettings()
        self.__comp7LightServerSettings.onServerSettingsChanged += self.__onServerSettingsChanged
        self.__updateProgressionSettings()

    def __clearServerSettings(self):
        if self.__comp7LightServerSettings is not None:
            self.__comp7LightServerSettings.onServerSettingsChanged -= self.__onServerSettingsChanged
            self.__comp7LightServerSettings.fini()
        self.__comp7LightServerSettings = None
        return

    def __onServerSettingsChanged(self, diff):
        if Configs.COMP7_LIGHT_CONFIG.value in diff:
            self.__resetTimer()
            self.__updateProgressionSettings()
            self.__applyRoleEquipmentOverrides()
            self.onModeConfigChanged()

    def __onCheckSceneChange(self):
        if not self.isModePrbActive():
            return
        self.__spaceSwitchController.hangarSpaceUpdate(COMP7_LIGHT_SCENE)

    @property
    def __roleEquipments(self):
        if not self.__roleEquipmentsCache:
            self.__roleEquipmentsCache = {}
            equipmentsCache = vehicles.g_cache.equipments()
            roleEquipmentsConfig = self.getModeSettings().roleEquipments
            for role, equipmentConfig in roleEquipmentsConfig.iteritems():
                if equipmentConfig['equipmentID'] is not None:
                    startCharge = equipmentConfig['startCharge']
                    startLevel = len([ levelCost for levelCost in equipmentConfig['cost'] if levelCost <= startCharge ])
                    self.__roleEquipmentsCache[role] = {'item': equipmentsCache[equipmentConfig['equipmentID']],
                     'startLevel': startLevel,
                     'overrides': equipmentConfig['overrides']}

        return self.__roleEquipmentsCache

    def __applyRoleEquipmentOverrides(self):
        equipmentsCache = vehicles.g_cache.equipments()
        roleEquipmentsConfig = self.getModeSettings().roleEquipments
        for equipment, overrideAttr in self.__roleOverridesCacheParameterByEquipment.iteritems():
            setattr(equipment, overrideAttr, None)

        self.__roleOverridesCacheParameterByEquipment = {}
        for equipmentConfig in roleEquipmentsConfig.itervalues():
            for attr, value in equipmentConfig['overrides'].iteritems():
                equipment = equipmentsCache[equipmentConfig['equipmentID']]
                overrideAttr = attr + 'RoleOverride'
                if hasattr(equipment, overrideAttr):
                    setattr(equipment, overrideAttr, value)
                    self.__roleOverridesCacheParameterByEquipment[equipment] = overrideAttr

        return
