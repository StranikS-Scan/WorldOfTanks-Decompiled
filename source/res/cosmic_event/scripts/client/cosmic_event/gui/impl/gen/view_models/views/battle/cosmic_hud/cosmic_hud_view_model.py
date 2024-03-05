# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/battle/cosmic_hud/cosmic_hud_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.ability_model import AbilityModel
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.artefact_scanning import ArtefactScanning
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.direction_marker_model import DirectionMarkerModel
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.marker_model import MarkerModel
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.player_record_model import PlayerRecordModel
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.vehicle_marker_model import VehicleMarkerModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.scoring_model import ScoringModel

class AnnouncementTypeEnum(Enum):
    NONE = 'none'
    AWAITINGPLAYERS = 'awaiting_players'
    CUSTOM = 'custom'
    PREBATTLE = 'pre_battle'
    STARTBATTLE = 'start_battle'
    PICKUPS = 'pickups'
    RESPAWN = 'respawn'
    PREPARETOSCAN = 'prepare_to_scan'
    SCANAVAILABLE = 'scan_available'
    PREPARETOSCANFINAL = 'prepare_to_scan_final'
    FINALSCANAVAILABLE = 'final_scan_available'
    SCANNING = 'scanning'
    MISSIONCOMPLETED = 'mission_completed'


class ArenaPhaseEnum(Enum):
    PREBATTLE = 'pre_battle'
    PHASE1 = 'phase_1'
    PHASE2 = 'phase_2'


class CosmicHudViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=22, commands=0):
        super(CosmicHudViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def crosshair(self):
        return self._getViewModel(0)

    @staticmethod
    def getCrosshairType():
        return MarkerModel

    @property
    def aim(self):
        return self._getViewModel(1)

    @staticmethod
    def getAimType():
        return MarkerModel

    @property
    def poiMarker(self):
        return self._getViewModel(2)

    @staticmethod
    def getPoiMarkerType():
        return DirectionMarkerModel

    @property
    def artefactScanning(self):
        return self._getViewModel(3)

    @staticmethod
    def getArtefactScanningType():
        return ArtefactScanning

    def getVehicleMarkers(self):
        return self._getArray(4)

    def setVehicleMarkers(self, value):
        self._setArray(4, value)

    @staticmethod
    def getVehicleMarkersType():
        return VehicleMarkerModel

    def getArenaTimeLeft(self):
        return self._getReal(5)

    def setArenaTimeLeft(self, value):
        self._setReal(5, value)

    def getArenaPhase(self):
        return ArenaPhaseEnum(self._getString(6))

    def setArenaPhase(self, value):
        self._setString(6, value.value)

    def getReloadTimeLeft(self):
        return self._getReal(7)

    def setReloadTimeLeft(self, value):
        self._setReal(7, value)

    def getReloadTime(self):
        return self._getReal(8)

    def setReloadTime(self, value):
        self._setReal(8, value)

    def getAnnouncementType(self):
        return AnnouncementTypeEnum(self._getString(9))

    def setAnnouncementType(self, value):
        self._setString(9, value.value)

    def getAnnouncementSecondsToEvent(self):
        return self._getNumber(10)

    def setAnnouncementSecondsToEvent(self, value):
        self._setNumber(10, value)

    def getAnnouncementCustomTitle(self):
        return self._getString(11)

    def setAnnouncementCustomTitle(self, value):
        self._setString(11, value)

    def getAnnouncementCustomSubtitle(self):
        return self._getString(12)

    def setAnnouncementCustomSubtitle(self, value):
        self._setString(12, value)

    def getPlayerName(self):
        return self._getString(13)

    def setPlayerName(self, value):
        self._setString(13, value)

    def getPlayerList(self):
        return self._getArray(14)

    def setPlayerList(self, value):
        self._setArray(14, value)

    @staticmethod
    def getPlayerListType():
        return PlayerRecordModel

    def getMessages(self):
        return self._getArray(15)

    def setMessages(self, value):
        self._setArray(15, value)

    @staticmethod
    def getMessagesType():
        return ScoringModel

    def getAbilities(self):
        return self._getArray(16)

    def setAbilities(self, value):
        self._setArray(16, value)

    @staticmethod
    def getAbilitiesType():
        return AbilityModel

    def getIsRespawning(self):
        return self._getBool(17)

    def setIsRespawning(self, value):
        self._setBool(17, value)

    def getShowPoiMarker(self):
        return self._getBool(18)

    def setShowPoiMarker(self, value):
        self._setBool(18, value)

    def getIsTargeting(self):
        return self._getBool(19)

    def setIsTargeting(self, value):
        self._setBool(19, value)

    def getAbilityDuration(self):
        return self._getNumber(20)

    def setAbilityDuration(self, value):
        self._setNumber(20, value)

    def getVehicleOverturned(self):
        return self._getBool(21)

    def setVehicleOverturned(self, value):
        self._setBool(21, value)

    def _initialize(self):
        super(CosmicHudViewModel, self)._initialize()
        self._addViewModelProperty('crosshair', MarkerModel())
        self._addViewModelProperty('aim', MarkerModel())
        self._addViewModelProperty('poiMarker', DirectionMarkerModel())
        self._addViewModelProperty('artefactScanning', ArtefactScanning())
        self._addArrayProperty('vehicleMarkers', Array())
        self._addRealProperty('arenaTimeLeft', 0.0)
        self._addStringProperty('arenaPhase', ArenaPhaseEnum.PREBATTLE.value)
        self._addRealProperty('reloadTimeLeft', 0.0)
        self._addRealProperty('reloadTime', 0.0)
        self._addStringProperty('announcementType', AnnouncementTypeEnum.NONE.value)
        self._addNumberProperty('announcementSecondsToEvent', -1)
        self._addStringProperty('announcementCustomTitle', '')
        self._addStringProperty('announcementCustomSubtitle', '')
        self._addStringProperty('playerName', '')
        self._addArrayProperty('playerList', Array())
        self._addArrayProperty('messages', Array())
        self._addArrayProperty('abilities', Array())
        self._addBoolProperty('isRespawning', False)
        self._addBoolProperty('showPoiMarker', False)
        self._addBoolProperty('isTargeting', False)
        self._addNumberProperty('abilityDuration', 0)
        self._addBoolProperty('vehicleOverturned', False)
