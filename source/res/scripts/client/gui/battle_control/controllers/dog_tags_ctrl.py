# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/dog_tags_ctrl.py
import logging
import weakref
import Math
import BigWorld
import Event
import PlayerEvents
import CGF
import GenericComponents
from UIComponents import GamefaceMarkerComponent
from AvatarInputHandler import cameras
from constants import ARENA_PERIOD
from account_helpers.settings_core.settings_constants import GAME
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from dog_tags_common.player_dog_tag import PlayerDogTag
from dog_tags_common.config.common import ComponentViewType
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)
_MARKER_VISIBLE_DISTANCE_ = 150.0
_MARKER_HEIGHT_ = 10.5
_MARKER_INTERVAL_ = 1.5
_MARKER_INITIAL_DELAY_ = 5.0

class DogTagsController(IBattleController):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, setup):
        super(DogTagsController, self).__init__()
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__isEnabled = self.lobbyContext.getServerSettings().isDogTagInBattleEnabled()
        self.__eManager = Event.EventManager()
        self.__pendingVehicles = []
        self.__dogTagGOs = {}
        self.__delayer = CallbackDelayer()
        self.onArenaVehicleVictimDogTagUpdated = Event.Event(self.__eManager)
        self.onKillerDogTagSet = Event.Event(self.__eManager)
        self.onVictimDogTagSet = Event.Event(self.__eManager)
        self.onKillerDogTagCheat = Event.Event(self.__eManager)

    def setKillerDogTag(self, killerDogTag):
        showKillersDogTag = bool(self.settingsCore.getSetting(GAME.SHOW_KILLERS_DOGTAG))
        if not self.__isEnabled or not showKillersDogTag:
            return
        _logger.info('DogTagsController.setKillerDogTag: killerDogTag %s', str(killerDogTag))
        killerDogTag = self._extendDogTagInfo([killerDogTag])[0]
        self.onKillerDogTagSet(killerDogTag)

    def setVictimsDogTags(self, victimsDogTags):
        showVictimsDogTag = bool(self.settingsCore.getSetting(GAME.SHOW_VICTIMS_DOGTAG))
        if not self.__isEnabled or not showVictimsDogTag:
            return
        _logger.info('DogTagsController.setVictimsDogTags: victimsDogTags %s', str(victimsDogTags))
        victimsDogTags = self._extendDogTagInfo(victimsDogTags)
        self._updateArenaVehicleVictimsDogTags(victimsDogTags)
        for victimDogTag in victimsDogTags:
            if victimDogTag['dogTag']['playerName']:
                self.onVictimDogTagSet(victimDogTag)

    def _initDogTagsInfo(self, vehicle):
        if not self.__isEnabled:
            return
        else:
            dogTagComponent = getattr(vehicle, 'dogTagComponent', None)
            if dogTagComponent:
                self._updateArenaVehicleVictimsDogTags(self._extendDogTagInfo(dogTagComponent.victimsDogTags))
                if dogTagComponent.killerDogTag.vehicleId != 0:
                    self.setKillerDogTag(dogTagComponent.killerDogTag)
            return

    def _updateArenaVehicleVictimsDogTags(self, victimsDogTags):
        if not self.lobbyContext.getServerSettings().isDogTagInBattleEnabled():
            return
        _logger.info('DogTagsController._updateArenaVehicleVictimsDogTags: victimsDogTags %s', str(victimsDogTags))
        for victimDogTag in victimsDogTags:
            flags, vo = self.__arenaDP.updateVehicleDogTag(victimDogTag['vehicleId'], victimDogTag)
            self.onArenaVehicleVictimDogTagUpdated(flags, vo, self.__arenaDP)

    def getControllerID(self):
        return BATTLE_CTRL_ID.DOG_TAGS

    def startControl(self):
        arenaSubscription = self.guiSessionProvider.arenaVisitor.getArenaSubscription()
        if arenaSubscription is not None:
            arenaSubscription.onPeriodChange += self.__onArenaPeriodChange
        avatar = BigWorld.player()
        avatar.onVehicleEnterWorld += self.__onVehicleEnterWorld
        avatar.onVehicleLeaveWorld += self.__onVehicleLeaveWorld
        PlayerEvents.g_playerEvents.onAvatarReady += self.__onAvatarReady
        if avatar.vehicle is not None:
            self._initDogTagsInfo(avatar.vehicle)
        return

    def stopControl(self):
        arenaSubscription = self.guiSessionProvider.arenaVisitor.getArenaSubscription()
        if arenaSubscription is not None:
            arenaSubscription.onPeriodChange -= self.__onArenaPeriodChange
        avatar = BigWorld.player()
        avatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld
        avatar.onVehicleLeaveWorld -= self.__onVehicleLeaveWorld
        PlayerEvents.g_playerEvents.onAvatarReady -= self.__onAvatarReady
        self.__clearMarkers()
        self.__eManager.clear()
        self.__eManager = None
        self.__arenaDP = None
        return

    def __onVehicleEnterWorld(self, vehicle):
        if self.guiSessionProvider.getArenaDP().isObserver(vehicle.id):
            return
        if vehicle.id == avatar_getter.getPlayerVehicleID():
            self._initDogTagsInfo(vehicle)
            if bool(self.settingsCore.getSetting(GAME.SHOW_PERSONAL_ANIMATED_DOGTAG)):
                self.__addDogTagMarker(vehicle)
        else:
            self.__addDogTagMarker(vehicle)

    def __onVehicleLeaveWorld(self, vehicle):
        self.__removeDogTagMarker(vehicle)

    def __onAvatarReady(self):
        if self.__canShowMarkers():
            self.__delayer.delayCallback(_MARKER_INITIAL_DELAY_, self.__processVehicles)

    def _extendDogTagInfo(self, dogTagsInfo):
        result = []
        arenaDP = self.guiSessionProvider.getArenaDP()
        for dogTagInfo in dogTagsInfo:
            vehicleId = dogTagInfo['vehicleId']
            vInfo = arenaDP.getVehicleInfo(vehicleId)
            playerName = vInfo.player.name
            playerClanAbbrev = vInfo.player.clanAbbrev
            dtInfoExt = {'vehicleId': vehicleId,
             'dogTag': {'components': dogTagInfo['dogTag']['components'],
                        'playerName': playerName if playerName else '',
                        'clanTag': playerClanAbbrev if playerClanAbbrev else ''}}
            result.append(dtInfoExt)

        return result

    def __addDogTagMarker(self, vehicle):
        if not self.__canShowMarkers():
            return
        dogTag = PlayerDogTag.fromDict(vehicle.dogTag['dogTag'])
        backgroundInfo = dogTag.getComponentByType(ComponentViewType.BACKGROUND).componentDefinition
        engravingInfo = dogTag.getComponentByType(ComponentViewType.ENGRAVING).componentDefinition
        if not backgroundInfo.isShowInPrebattle or not engravingInfo.isShowInPrebattle:
            return
        self.__pendingVehicles.append(vehicle)

    def __removeDogTagMarker(self, vehicle):
        if vehicle.id in self.__dogTagGOs:
            CGF.removeGameObject(self.__dogTagGOs[vehicle.id])
            self.__dogTagGOs.pop(vehicle.id)
        if vehicle in self.__pendingVehicles:
            self.__pendingVehicles.remove(vehicle)

    def __onArenaPeriodChange(self, period, *_):
        if period >= ARENA_PERIOD.BATTLE:
            self.__clearMarkers()

    def __canShowMarkers(self):
        return self.__isEnabled and self.guiSessionProvider.arenaVisitor.getArenaPeriod() < ARENA_PERIOD.BATTLE and self.lobbyContext.getServerSettings().isDogTagsBattleMarkerEnabled()

    def __clearMarkers(self):
        for _, dogTagGO in self.__dogTagGOs.items():
            CGF.removeGameObject(dogTagGO)

        self.__dogTagGOs = {}
        self.__pendingVehicles = []
        self.__delayer.stopCallback(self.__processVehicles)

    def __processVehicles(self):
        for vehicle in self.__pendingVehicles:
            if cameras.isPointOnScreen(vehicle.position):
                dogTagGO = CGF.GameObject(BigWorld.player().spaceID)
                dogTagGO.createComponent(GamefaceMarkerComponent, 'DogTagMarkerView', 'gui.impl.battle.dog_tags.dog_tag_marker_view', vehicle.id, _MARKER_VISIBLE_DISTANCE_)
                dogTagGO.createComponent(GenericComponents.TransformComponent, vehicle.position + Math.Vector3(0, _MARKER_HEIGHT_, 0))
                dogTagGO.activate()
                self.__dogTagGOs[vehicle.id] = dogTagGO
                self.__pendingVehicles.remove(vehicle)
                break

        return _MARKER_INTERVAL_
