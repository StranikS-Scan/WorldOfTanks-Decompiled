# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/helpers/comp7_light_server_settings.py
import logging
from collections import namedtuple
from shared_utils import makeTupleByDict
import BattleReplay
from Event import Event
from Event import EventManager
from comp7_light_constants import Configs
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class _Comp7LightConfig(namedtuple('_Comp7LightConfig', ('isEnabled', 'isTrainingEnabled', 'peripheryIDs', 'primeTimes', 'seasons', 'cycleTimes', 'battleModifiersDescr', 'maps', 'levels', 'numPlayers', 'squadSizes', 'forbiddenClassTags', 'forbiddenVehTypes', 'roleEquipments', 'poiEquipments', 'createVivoxTeamChannels', 'tournaments', 'progression'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, isTrainingEnabled=False, peripheryIDs={}, primeTimes={}, seasons={}, cycleTimes={}, battleModifiersDescr=(), maps=set(), levels=[], numPlayers=7, squadSizes=[0, 0], forbiddenClassTags=set(), forbiddenVehTypes=set(), roleEquipments={}, poiEquipments={}, createVivoxTeamChannels=False, tournaments={}, progression={})
        defaults.update(kwargs)
        return super(_Comp7LightConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class Comp7LightServerSettings(object):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(Comp7LightServerSettings, self).__init__()
        self.__comp7LightConfig = _Comp7LightConfig()
        self.__serverSettings = self.__lobbyContext.getServerSettings()
        self.__setInitialValues()
        self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange += self.__update
        self.__eventsManager = EventManager()
        self.onServerSettingsChanged = Event(self.__eventsManager)
        return

    @property
    def comp7LightConfig(self):
        return self.__comp7LightConfig

    def fini(self):
        self.__comp7LightConfig = None
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__update
        self.__serverSettings = None
        self.__eventsManager.clear()
        return

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__update
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__update
        return

    def __setInitialValues(self):
        settings = self.__serverSettings.getSettings()
        if not settings and BattleReplay.isPlaying() and not BattleReplay.isServerSideReplay():
            settings = BattleReplay.g_replayCtrl.arenaInfo['serverSettings']
        if Configs.COMP7_LIGHT_CONFIG.value in settings:
            _logger.debug(Configs.COMP7_LIGHT_CONFIG.value, settings[Configs.COMP7_LIGHT_CONFIG.value])
            self.__comp7LightConfig = makeTupleByDict(_Comp7LightConfig, settings[Configs.COMP7_LIGHT_CONFIG.value])
        else:
            self.__comp7LightConfig = _Comp7LightConfig.defaults()

    def __update(self, serverSettingsDiff):
        if Configs.COMP7_LIGHT_CONFIG.value in serverSettingsDiff:
            self.__comp7LightConfig = self.__comp7LightConfig.replace(serverSettingsDiff[Configs.COMP7_LIGHT_CONFIG.value])
            self.onServerSettingsChanged(serverSettingsDiff)
