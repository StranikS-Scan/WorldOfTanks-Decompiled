# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/gui/game_control/museum_of_glory_controller.py
from sys import maxint
from museum_of_glory_account_settings import getMuseumOfGlorySetting, setMuseumOfGlorySettings
from museum_of_glory.museum_of_glory_constants import ALL_VEHS_INT_CD, NEW_CONTENT, VEHS_COUNT
from museum_of_glory.museum_of_glory_constants import MUSEUM_OF_GLORY_CONFIG
from Event import Event, EventManager
from helpers import dependency, server_settings
from helpers.events_handler import EventsHandler
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IMuseumOfGloryController
from gui.shared.gui_items.vehicle_modules import VehicleGun, VehicleTurret, VehicleChassis
from gui.shared.gui_items.Vehicle import Vehicle
from items import vehicles
from gui.shared.gui_items import vehicle_adjusters
from museum_of_glory.museum_of_glory_constants import CHARACTERISTIC_FIELDS
from museum_of_glory.dto.vehicle import VehicleDto
from wotdecorators import noexcept

class MuseumOfGloryController(IMuseumOfGloryController, EventsHandler):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__eventManager = EventManager()
        self.onConfigUpdate = Event(self.__eventManager)
        self.__config = None
        self.__vehDto = list()
        self.__minYear = maxint
        self.__vehSet = set()
        self.__vehCount = 0
        return

    def onLobbyInited(self, _):
        self.__config = self.__lobbyContext.getServerSettings().getMuseumOfGloryConfig()
        self.__update()
        self._subscribe()

    def onAccountBecomeNonPlayer(self):
        self.__config = None
        self.__vehDto = []
        self.__minYear = None
        self._unsubscribe()
        self.__eventManager.clear()
        return

    @property
    def isEnabled(self):
        return bool(self.__vehDto)

    def getEpochMusics(self, year):
        return self.__config['epochMusics'].get(year)

    def getVehiclesDto(self):
        return self.__vehDto

    def getBackgroundImage(self, year):
        return self.__config['backgrounds'][year]

    def getMinYear(self):
        return self.__minYear

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),)

    @server_settings.serverSettingsChangeListener(MUSEUM_OF_GLORY_CONFIG)
    def __onServerSettingsChanged(self, _=None):
        self.__update()

    def __update(self):
        self.__createVehicleList()
        self.onConfigUpdate()

    @noexcept
    def __createVehicleList(self):
        self.__vehDto = []
        self.__minYear = maxint
        self.__vehSet = set()
        self.__vehCount = 0
        if not self.__lobbyContext.getServerSettings().getMuseumOfGloryConfig().get('isEnabled'):
            return
        else:
            self.__config = self.__lobbyContext.getServerSettings().getMuseumOfGloryConfig()
            for el in self.__config['tanksConfig']:
                tank, items = next(el.iteritems())
                specs = items['specs']
                year = items['epoch']
                voiceoverLength = items['voiceoverLength']
                self.__minYear = min(self.__minYear, year)
                descr = {}
                for i, spec in enumerate(specs):
                    descr[CHARACTERISTIC_FIELDS[i]] = spec

                notFittedReason = None
                vehTypeCompDesc = vehicles.makeVehicleTypeCompDescrByName(tank)
                vehicle = Vehicle(typeCompDescr=vehTypeCompDesc)
                newGunItem = next((gun for gun in vehicle.typeDescr.getGuns() if gun.name == items.get('vehicleGun')), None)
                newTurretItem = next((turret for turret in vehicle.typeDescr.turrets[0] if turret.name == items.get('vehicleTurret')), None)
                newChassisItem = next((chassis for chassis in vehicle.typeDescr.chassis if chassis.name == items.get('vehicleChassis')), None)
                newGun = VehicleGun(intCompactDescr=newGunItem.compactDescr, descriptor=newGunItem) if newGunItem else vehicle.gun
                newTurret = VehicleTurret(intCompactDescr=newTurretItem.compactDescr, descriptor=newTurretItem) if newTurretItem else vehicle.turret
                newChassis = VehicleChassis(intCompactDescr=newChassisItem.compactDescr, descriptor=newChassisItem) if newChassisItem else vehicle.chassis
                modules = (newTurret, newGun, newChassis)
                vehicle_adjusters.installModulesSet(vehicle, list(modules[:]), notFittedReason)
                veh = VehicleDto(vehicle=vehicle, intCD=vehicle.intCD, name=vehicle.name, strCD=vehicle.descriptor.makeCompactDescr(), year=year, description=descr, voiceoverLength=voiceoverLength)
                self.__vehSet.add(vehicle.intCD)
                self.__vehCount += 1
                self.__vehDto.append(veh)

            self.__checkIsNewContentAvailable()
            return

    def __checkIsNewContentAvailable(self):
        if getMuseumOfGlorySetting(ALL_VEHS_INT_CD) != self.__vehSet or getMuseumOfGlorySetting(VEHS_COUNT) != self.__vehCount:
            setMuseumOfGlorySettings(NEW_CONTENT, True)
            setMuseumOfGlorySettings(ALL_VEHS_INT_CD, self.__vehSet)
            setMuseumOfGlorySettings(VEHS_COUNT, self.__vehCount)
