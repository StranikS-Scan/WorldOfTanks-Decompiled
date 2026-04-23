# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/battle_control/controllers/comp7_vehicle_ban_ctrl.py
import BigWorld
from comp7_core_constants import ArenaPrebattlePhase
from comp7_core.gui.comp7_core_constants import BATTLE_CTRL_ID
from Event import EventManager, Event
from gui.battle_control.controllers.interfaces import IBattleController

class Comp7VehicleBanController(IBattleController):

    def __init__(self):
        super(Comp7VehicleBanController, self).__init__()
        self.__eventsManager = EventManager()
        self.onVehicleBanStateUpdated = Event(self.__eventsManager)
        self.onCandidatesForBanUpdated = Event(self.__eventsManager)
        self.onBanPhaseUpdated = Event(self.__eventsManager)
        self.__isVehicleBanEnabled = False
        self.__vehiclePrepickEndTime = 0.0
        self.__vehicleBanEndTime = 0.0
        self.__currentPrebattlePhase = None
        self.__vehiclesListForBan = []
        self.__playersChoiceForBan = dict()
        self.__bannedVehicles = dict()
        self.__candidatesForBan = dict()
        self.__vehicleCopiesInfo = dict()
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.COMP7_VEHICLE_BAN_CTRL

    def startControl(self, *_):
        pass

    def stopControl(self):
        self.__eventsManager.clear()
        self.__isVehicleBanEnabled = False
        self.__vehiclePrepickEndTime = 0.0
        self.__vehicleBanEndTime = 0.0
        self.__currentPrebattlePhase = None
        self.__vehiclesListForBan[:] = []
        self.__playersChoiceForBan.clear()
        self.__bannedVehicles.clear()
        self.__candidatesForBan.clear()
        self.__vehicleCopiesInfo.clear()
        return

    @property
    def isVehicleBanEnabled(self):
        return self.__isVehicleBanEnabled

    @property
    def vehiclePrepickEndTime(self):
        return self.__vehiclePrepickEndTime

    @property
    def vehicleBanEndTime(self):
        return self.__vehicleBanEndTime

    @property
    def vehiclesListForBan(self):
        return self.__vehiclesListForBan

    @property
    def bannedVehicles(self):
        return self.__bannedVehicles

    @property
    def candidatesForBan(self):
        return self.__candidatesForBan

    @isVehicleBanEnabled.setter
    def isVehicleBanEnabled(self, value):
        self.__isVehicleBanEnabled = value

    @vehiclePrepickEndTime.setter
    def vehiclePrepickEndTime(self, value):
        self.__vehiclePrepickEndTime = value
        self.__updatePhase()

    @vehicleBanEndTime.setter
    def vehicleBanEndTime(self, value):
        self.__vehicleBanEndTime = value
        self.__updatePhase()

    @vehiclesListForBan.setter
    def vehiclesListForBan(self, vehiclesList):
        if not vehiclesList or vehiclesList == self.__vehiclesListForBan:
            return
        self.__vehiclesListForBan[:] = list(vehiclesList)
        self.onVehicleBanStateUpdated()

    @bannedVehicles.setter
    def bannedVehicles(self, vehiclesList):
        self.__bannedVehicles = vehiclesList
        self.__updatePhase()

    @candidatesForBan.setter
    def candidatesForBan(self, candidates):
        self.__candidatesForBan = candidates
        self.onCandidatesForBanUpdated()

    def updatePlayersChoiceForBan(self, playersChoiceForBan):
        self.__playersChoiceForBan = playersChoiceForBan
        self.onVehicleBanStateUpdated()

    def getPlayerChoiceForBan(self, playerDatabaseID):
        vehicleCD, state = self.__playersChoiceForBan.get(playerDatabaseID, (None, False))
        return (vehicleCD, bool(state))

    def updateVehicleCopiesInfo(self, vehicleCopiesInfo):
        if not vehicleCopiesInfo:
            return
        self.__vehicleCopiesInfo.clear()
        self.__vehicleCopiesInfo.update(vehicleCopiesInfo)

    def getVehicleCopies(self, vehicleCD):
        return self.__vehicleCopiesInfo.get(vehicleCD, [])

    def chooseVehicleForBan(self, vehicleCD):
        BigWorld.player().AvatarComp7BaseComponent.chooseVehicleForBan(vehicleCD)

    def confirmBanVehicle(self):
        BigWorld.player().AvatarComp7BaseComponent.confirmBanVehicle()

    def getArenaPrebattlePhase(self):
        if self.__bannedVehicles:
            return ArenaPrebattlePhase.PICK
        if not self.__vehiclePrepickEndTime and not self.__vehicleBanEndTime:
            return ArenaPrebattlePhase.NONE
        return ArenaPrebattlePhase.PREPICK if self.__vehiclePrepickEndTime and not self.__vehicleBanEndTime else ArenaPrebattlePhase.VOTING

    def __updatePhase(self):
        prebattlePhase = self.getArenaPrebattlePhase()
        if prebattlePhase != self.__currentPrebattlePhase:
            self.__currentPrebattlePhase = prebattlePhase
            self.onBanPhaseUpdated()
