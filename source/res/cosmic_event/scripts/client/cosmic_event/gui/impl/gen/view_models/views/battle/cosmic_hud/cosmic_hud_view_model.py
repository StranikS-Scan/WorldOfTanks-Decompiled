# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/battle/cosmic_hud/cosmic_hud_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.ability_model import AbilityModel
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.cosmic_progress_bar import CosmicProgressBar
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.direction_marker_model import DirectionMarkerModel
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.loot_marker_model import LootMarkerModel
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.marker_model import MarkerModel
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.player_record_model import PlayerRecordModel
from cosmic_event.gui.impl.gen.view_models.views.battle.cosmic_hud.super_loot_scanning import SuperLootScanning
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
    PREPARETOLOOTPICKUP = 'prepare_to_loot_pickup'


class ArenaPhaseEnum(Enum):
    PREBATTLE = 'pre_battle'
    PHASE1 = 'phase_1'
    PHASE2 = 'phase_2'


class CosmicHudViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=25, commands=0):
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
    def lootMarker(self):
        return self._getViewModel(2)

    @staticmethod
    def getLootMarkerType():
        return LootMarkerModel

    @property
    def superLootScanning(self):
        return self._getViewModel(3)

    @staticmethod
    def getSuperLootScanningType():
        return SuperLootScanning

    def getVehicleMarkers(self):
        return self._getArray(4)

    def setVehicleMarkers(self, value):
        self._setArray(4, value)

    @staticmethod
    def getVehicleMarkersType():
        return VehicleMarkerModel

    def getPoiMarkers(self):
        return self._getArray(5)

    def setPoiMarkers(self, value):
        self._setArray(5, value)

    @staticmethod
    def getPoiMarkersType():
        return DirectionMarkerModel

    def getProgressBars(self):
        return self._getArray(6)

    def setProgressBars(self, value):
        self._setArray(6, value)

    @staticmethod
    def getProgressBarsType():
        return CosmicProgressBar

    def getArenaTimeLeft(self):
        return self._getReal(7)

    def setArenaTimeLeft(self, value):
        self._setReal(7, value)

    def getArenaPhase(self):
        return ArenaPhaseEnum(self._getString(8))

    def setArenaPhase(self, value):
        self._setString(8, value.value)

    def getReloadTimeLeft(self):
        return self._getReal(9)

    def setReloadTimeLeft(self, value):
        self._setReal(9, value)

    def getReloadTime(self):
        return self._getReal(10)

    def setReloadTime(self, value):
        self._setReal(10, value)

    def getAnnouncementType(self):
        return AnnouncementTypeEnum(self._getString(11))

    def setAnnouncementType(self, value):
        self._setString(11, value.value)

    def getAnnouncementSecondsToEvent(self):
        return self._getNumber(12)

    def setAnnouncementSecondsToEvent(self, value):
        self._setNumber(12, value)

    def getAnnouncementCustomTitle(self):
        return self._getString(13)

    def setAnnouncementCustomTitle(self, value):
        self._setString(13, value)

    def getAnnouncementCustomSubtitle(self):
        return self._getString(14)

    def setAnnouncementCustomSubtitle(self, value):
        self._setString(14, value)

    def getPlayerName(self):
        return self._getString(15)

    def setPlayerName(self, value):
        self._setString(15, value)

    def getPlayerList(self):
        return self._getArray(16)

    def setPlayerList(self, value):
        self._setArray(16, value)

    @staticmethod
    def getPlayerListType():
        return PlayerRecordModel

    def getMessages(self):
        return self._getArray(17)

    def setMessages(self, value):
        self._setArray(17, value)

    @staticmethod
    def getMessagesType():
        return ScoringModel

    def getAbilities(self):
        return self._getArray(18)

    def setAbilities(self, value):
        self._setArray(18, value)

    @staticmethod
    def getAbilitiesType():
        return AbilityModel

    def getIsRespawning(self):
        return self._getBool(19)

    def setIsRespawning(self, value):
        self._setBool(19, value)

    def getShowLootMarker(self):
        return self._getBool(20)

    def setShowLootMarker(self, value):
        self._setBool(20, value)

    def getIsTargeting(self):
        return self._getBool(21)

    def setIsTargeting(self, value):
        self._setBool(21, value)

    def getAbilityDuration(self):
        return self._getNumber(22)

    def setAbilityDuration(self, value):
        self._setNumber(22, value)

    def getVehicleOverturned(self):
        return self._getBool(23)

    def setVehicleOverturned(self, value):
        self._setBool(23, value)

    def getSelectedVehicleID(self):
        return self._getNumber(24)

    def setSelectedVehicleID(self, value):
        self._setNumber(24, value)

    def _initialize(self):
        super(CosmicHudViewModel, self)._initialize()
        self._addViewModelProperty('crosshair', MarkerModel())
        self._addViewModelProperty('aim', MarkerModel())
        self._addViewModelProperty('lootMarker', LootMarkerModel())
        self._addViewModelProperty('superLootScanning', SuperLootScanning())
        self._addArrayProperty('vehicleMarkers', Array())
        self._addArrayProperty('poiMarkers', Array())
        self._addArrayProperty('progressBars', Array())
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
        self._addBoolProperty('showLootMarker', False)
        self._addBoolProperty('isTargeting', False)
        self._addNumberProperty('abilityDuration', 0)
        self._addBoolProperty('vehicleOverturned', False)
        self._addNumberProperty('selectedVehicleID', 0)
