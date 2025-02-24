# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/helpers/comp7_server_settings.py
import copy
import logging
from shared_utils import makeTupleByDict
from Event import Event
from Event import EventManager
from comp7_common.comp7_constants import Configs
from comp7_ranks_common import Comp7Division
from helpers import dependency
from helpers.server_settings import settingsBlock
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class _Comp7QualificationConfig(settingsBlock('_Comp7QualificationConfig', ('battlesNumber',))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return {'battlesNumber': 0}


class Comp7Config(settingsBlock('Comp7Config', ('isEnabled', 'isShopEnabled', 'isTrainingEnabled', 'peripheryIDs', 'primeTimes', 'seasons', 'battleModifiersDescr', 'cycleTimes', 'roleEquipments', 'poiEquipments', 'numPlayers', 'levels', 'forbiddenClassTags', 'forbiddenVehTypes', 'squadRankRestriction', 'squadSizes', 'createVivoxTeamChannels', 'qualification', 'maps', 'tournaments', 'grandTournament', 'remainingOfferTokensNotifications', 'clientEntitlementsCache', 'participantTokens'))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return dict(isEnabled=False, isShopEnabled=False, isTrainingEnabled=False, peripheryIDs={}, primeTimes={}, seasons={}, battleModifiersDescr=(), cycleTimes={}, roleEquipments={}, poiEquipments={}, numPlayers=7, levels=[], forbiddenClassTags=set(), forbiddenVehTypes=set(), squadRankRestriction={}, squadSizes=[0, 0], createVivoxTeamChannels=False, qualification={}, maps=set(), tournaments={}, grandTournament={}, remainingOfferTokensNotifications=[], clientEntitlementsCache={}, participantTokens=())

    @classmethod
    def _preprocessData(cls, data):
        qualificationConfig = data.get('qualification')
        if qualificationConfig is not None:
            data['qualification'] = makeTupleByDict(_Comp7QualificationConfig, qualificationConfig)
        return data


class Comp7RanksConfig(settingsBlock('Comp7RanksConfig', ('ranks', 'ranksOrder', 'eliteRankPercent', 'divisionsByRank', 'divisions', 'rankInactivityNotificationThreshold'))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return dict(ranks={}, ranksOrder=(), eliteRankPercent=0, divisionsByRank={}, divisions=(), rankInactivityNotificationThreshold=0)

    @classmethod
    def _preprocessData(cls, data):
        divisions = data.get('divisions')
        if divisions:
            data['divisions'] = cls.__dictDivisionsToComp7Divisions(divisions)
        divisionsByRank = data.get('divisionsByRank')
        if divisionsByRank:
            for rankID, divisions in divisionsByRank.iteritems():
                data['divisionsByRank'][rankID] = cls.__dictDivisionsToComp7Divisions(divisions)

        return data

    @classmethod
    def __dictDivisionsToComp7Divisions(cls, divisions):
        return tuple((Comp7Division(serialIdx, divisionInfo) for serialIdx, divisionInfo in enumerate(divisions)))


class Comp7RewardsConfig(settingsBlock('Comp7RewardsConfig', ('main', 'extra'))):
    __slots__ = ()

    @classmethod
    def defaults(cls):
        return {'main': [],
         'extra': []}


class Comp7ServerSettings(object):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(Comp7ServerSettings, self).__init__()
        self.__comp7Config = Comp7Config()
        self.__comp7RanksConfig = Comp7RanksConfig()
        self.__comp7RewardsConfig = Comp7RewardsConfig()
        self.__serverSettings = self.__lobbyContext.getServerSettings()
        self.__setInitValues()
        self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange += self.__update
        self.__eventsManager = EventManager()
        self.onComp7SettingsChanged = Event(self.__eventsManager)
        return

    @property
    def comp7Config(self):
        return self.__comp7Config

    @property
    def comp7RanksConfig(self):
        return self.__comp7RanksConfig

    @property
    def comp7RewardsConfig(self):
        return self.__comp7RewardsConfig

    def fini(self):
        self.__comp7Config = None
        self.__comp7RanksConfig = None
        self.__comp7RewardsConfig = None
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

    def __setInitValues(self):
        settings = self.__serverSettings.getSettings() if self.__serverSettings else {}
        if Configs.COMP7_CONFIG.value in settings:
            _logger.debug(Configs.COMP7_CONFIG.value, settings[Configs.COMP7_CONFIG.value])
            self.__comp7Config = makeTupleByDict(Comp7Config, settings[Configs.COMP7_CONFIG.value])
        else:
            self.__comp7Config = makeTupleByDict(Comp7Config, Comp7Config.defaults())
        if Configs.COMP7_RANKS_CONFIG.value in settings:
            _logger.debug(Configs.COMP7_RANKS_CONFIG.value, settings[Configs.COMP7_RANKS_CONFIG.value])
            self.__comp7RanksConfig = makeTupleByDict(Comp7RanksConfig, settings[Configs.COMP7_RANKS_CONFIG.value])
        else:
            self.__comp7RanksConfig = makeTupleByDict(Comp7RanksConfig, Comp7RanksConfig.defaults())
        if Configs.COMP7_REWARDS_CONFIG.value in settings:
            _logger.debug(Configs.COMP7_REWARDS_CONFIG.value, settings[Configs.COMP7_REWARDS_CONFIG.value])
            self.__comp7RewardsConfig = makeTupleByDict(Comp7RewardsConfig, settings[Configs.COMP7_REWARDS_CONFIG.value])
        else:
            self.__comp7RewardsConfig = makeTupleByDict(Comp7RewardsConfig, Comp7RewardsConfig.defaults())

    def __update(self, serverSettingsDiff):
        if Configs.COMP7_CONFIG.value in serverSettingsDiff:
            self.__updateComp7(serverSettingsDiff)
        if Configs.COMP7_RANKS_CONFIG.value in serverSettingsDiff:
            self.__updateComp7PrestigeRanks(serverSettingsDiff)
        if Configs.COMP7_REWARDS_CONFIG.value in serverSettingsDiff:
            self.__updateComp7Rewards(serverSettingsDiff)

    def __updateComp7(self, targetSettings):
        config = targetSettings[Configs.COMP7_CONFIG.value]
        self.__comp7Config = self.__comp7Config.replace(copy.deepcopy(config))
        self.onComp7SettingsChanged(targetSettings)

    def __updateComp7PrestigeRanks(self, targetSettings):
        config = targetSettings[Configs.COMP7_RANKS_CONFIG.value]
        self.__comp7RanksConfig = self.__comp7RanksConfig.replace(copy.deepcopy(config))
        self.onComp7SettingsChanged(targetSettings)

    def __updateComp7Rewards(self, targetSettings):
        config = targetSettings[Configs.COMP7_REWARDS_CONFIG.value]
        self.__comp7RewardsConfig = self.__comp7RewardsConfig.replace(config)
        self.onComp7SettingsChanged(targetSettings)
