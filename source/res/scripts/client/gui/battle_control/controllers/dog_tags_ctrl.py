# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/dog_tags_ctrl.py
import logging
import weakref
import BigWorld
import Event
from account_helpers.settings_core.settings_constants import GAME
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class DogTagsController(IBattleController):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, setup):
        super(DogTagsController, self).__init__()
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__isEnabled = self.lobbyContext.getServerSettings().isDogTagInBattleEnabled()
        self.__eManager = Event.EventManager()
        self.onArenaVehicleVictimDogTagUpdated = Event.Event(self.__eManager)
        self.onKillerDogTagSet = Event.Event(self.__eManager)
        self.onVictimDogTagSet = Event.Event(self.__eManager)
        self.onKillerDogTagCheat = Event.Event(self.__eManager)

    def setKillerDogTag(self, killerDogTag):
        if not self.__isEnabled:
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
        avatar = BigWorld.player()
        playerVehicle = avatar.vehicle
        if playerVehicle is not None:
            self._initDogTagsInfo(playerVehicle)
        else:
            avatar.onVehicleEnterWorld += self.__onVehicleEnterWorld
        return

    def stopControl(self):
        avatar = BigWorld.player()
        avatar.onVehicleEnterWorld -= self.__onVehicleEnterWorld

    def __onVehicleEnterWorld(self, vehicle):
        if vehicle.id == avatar_getter.getPlayerVehicleID():
            BigWorld.player().onVehicleEnterWorld -= self.__onVehicleEnterWorld
            self._initDogTagsInfo(vehicle)

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
