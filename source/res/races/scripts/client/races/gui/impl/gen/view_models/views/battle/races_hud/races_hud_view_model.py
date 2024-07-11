# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/battle/races_hud/races_hud_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from races.gui.impl.gen.view_models.views.battle.races_hud.ability_model import AbilityModel
from races.gui.impl.gen.view_models.views.battle.races_hud.direction_marker_model import DirectionMarkerModel
from races.gui.impl.gen.view_models.views.battle.races_hud.marker_model import MarkerModel
from races.gui.impl.gen.view_models.views.battle.races_hud.player_record_model import PlayerRecordModel
from races.gui.impl.gen.view_models.views.battle.races_hud.races_minimap_component_model import RacesMinimapComponentModel
from races.gui.impl.gen.view_models.views.battle.races_hud.vehicle_marker_model import VehicleMarkerModel
from races.gui.impl.gen.view_models.views.lobby.races_lobby_view.scoring_model import ScoringModel

class AnnouncementTypeEnum(Enum):
    NONE = 'none'
    AWAITINGPLAYERS = 'awaiting_players'
    CUSTOM = 'custom'
    PREBATTLE = 'pre_battle'
    STARTRACE = 'start_race'
    PICKUPS = 'pickups'
    MISSIONCOMPLETED = 'mission_completed'


class ArenaPhaseEnum(Enum):
    PREBATTLE = 'pre_battle'
    RACE = 'race'


class RacesHudViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=25, commands=0):
        super(RacesHudViewModel, self).__init__(properties=properties, commands=commands)

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
    def minimapComponent(self):
        return self._getViewModel(3)

    @staticmethod
    def getMinimapComponentType():
        return RacesMinimapComponentModel

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

    def getAbilityDuration(self):
        return self._getNumber(17)

    def setAbilityDuration(self, value):
        self._setNumber(17, value)

    def getVehicleOverturned(self):
        return self._getBool(18)

    def setVehicleOverturned(self, value):
        self._setBool(18, value)

    def getVehicleSpeed(self):
        return self._getNumber(19)

    def setVehicleSpeed(self, value):
        self._setNumber(19, value)

    def getIsVisibleHelpHint(self):
        return self._getBool(20)

    def setIsVisibleHelpHint(self, value):
        self._setBool(20, value)

    def getIsRaceFinished(self):
        return self._getBool(21)

    def setIsRaceFinished(self, value):
        self._setBool(21, value)

    def getIsArenaFinished(self):
        return self._getBool(22)

    def setIsArenaFinished(self, value):
        self._setBool(22, value)

    def getIsPrebattlePeriod(self):
        return self._getBool(23)

    def setIsPrebattlePeriod(self, value):
        self._setBool(23, value)

    def getPlayerTotalScore(self):
        return self._getNumber(24)

    def setPlayerTotalScore(self, value):
        self._setNumber(24, value)

    def _initialize(self):
        super(RacesHudViewModel, self)._initialize()
        self._addViewModelProperty('crosshair', MarkerModel())
        self._addViewModelProperty('aim', MarkerModel())
        self._addViewModelProperty('poiMarker', DirectionMarkerModel())
        self._addViewModelProperty('minimapComponent', RacesMinimapComponentModel())
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
        self._addNumberProperty('abilityDuration', 0)
        self._addBoolProperty('vehicleOverturned', False)
        self._addNumberProperty('vehicleSpeed', 0)
        self._addBoolProperty('isVisibleHelpHint', False)
        self._addBoolProperty('isRaceFinished', False)
        self._addBoolProperty('isArenaFinished', False)
        self._addBoolProperty('isPrebattlePeriod', False)
        self._addNumberProperty('playerTotalScore', 0)
