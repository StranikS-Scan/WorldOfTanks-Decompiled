# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/TrainingSettingsWindow.py
import ArenaType
from account_helpers import gameplay_ctx
from constants import PREBATTLE_TYPE, Configs
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.Scaleform.daapi.view.lobby.trainings import formatters
from gui.Scaleform.daapi.view.meta.TrainingWindowMeta import TrainingWindowMeta
from gui.prb_control import prbEntityProperty
from gui.prb_control.prb_getters import getTrainingBattleRoundLimits
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from helpers import i18n
from gui.impl import backport
from gui.impl.gen import R
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
def isComp7Arena(arena, settings, comp7Controller=None):
    if not comp7Controller.isTrainingEnabled() or settings.isDevBattle:
        return False
    comp7Config = comp7Controller.getModeSettings()
    return arena.geometryID in comp7Config.maps


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getComp7Data(lobbyContext=None):
    return {'size': lobbyContext.getServerSettings().comp7Config.numPlayers,
     'canChangeArenaTime': False,
     'alertText': backport.text(R.strings.menu.training.alertText.onlyTierX())}


_ARENA_TYPE_FILTERS = {'comp7': isComp7Arena}
_ARENA_TYPE_DATA_GETTERS = {'comp7': getComp7Data}

class ArenasCache(object):
    __lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx, settings):
        self.__cache = []
        self.__isEpic = ctx.get('isEpic', False)
        self.__settings = settings
        self.build()

    def fini(self):
        self.__cache = []

    @property
    def cache(self):
        return self.__cache

    def build(self):
        cache = []
        for arenaTypeID, arenaType in ArenaType.g_cache.iteritems():
            if not self.__isArenaSuitableForTraining(arenaType):
                continue
            try:
                arenaTypeName = self.__getArenaTypeName(arenaType)
                dataItem = {'label': '%s - %s' % (arenaType.name, arenaTypeName) if arenaTypeName else arenaType.name,
                 'name': arenaType.name,
                 'arenaType': arenaTypeName,
                 'key': arenaTypeID,
                 'size': arenaType.maxPlayersInTeam,
                 'time': arenaType.roundLength / 60,
                 'description': '',
                 'icon': formatters.getMapIconPath(arenaType),
                 'canChangeArenaTime': not self.__isEpic,
                 'alertText': ''}
                dataGetter = _ARENA_TYPE_DATA_GETTERS.get(arenaType.gameplayName)
                if dataGetter is not None:
                    dataItem.update(dataGetter())
                cache.append(dataItem)
            except Exception:
                LOG_ERROR('There is error while reading arenas cache', arenaTypeID, arenaType)
                LOG_CURRENT_EXCEPTION()
                continue

        self.__cache = sorted(cache, key=lambda x: (x['label'].lower(), x['name'].lower()))
        return

    def __getArenaTypeName(self, arena):
        if arena.gameplayName == 'ctf':
            return ''
        arenaGameplayName = '#arenas:type/%s/%s/name' % (arena.gameplayName, arena.geometryName)
        return i18n.makeString(arenaGameplayName) if i18n.doesTextExist(arenaGameplayName) else i18n.makeString('#arenas:type/%s/name' % arena.gameplayName)

    def __isArenaSuitableForTraining(self, arena):
        if arena.explicitRequestOnly:
            return False
        else:
            arenaTypeFilter = _ARENA_TYPE_FILTERS.get(arena.gameplayName)
            return arenaTypeFilter(arena, self.__settings) if arenaTypeFilter is not None and not self.__isEpic else gameplay_ctx.isCreationEnabled(arena.gameplayName, self.__isEpic)


class TrainingSettingsWindow(TrainingWindowMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __INFLUENCING_CONFIG_KEYS = {Configs.PRE_MODERATION_CONFIG.value, Configs.COMP7_CONFIG.value}

    def __init__(self, ctx=None):
        super(TrainingSettingsWindow, self).__init__()
        self.__isCreateRequest = ctx.get('isCreateRequest', False)
        self.__settings = ctx.get('settings', None)
        self.__isEpic = self.__settings.getEntityType() == PREBATTLE_TYPE.EPIC_TRAINING
        self.__arenasCache = ArenasCache({'isEpic': self.__isEpic}, self.__settings)
        return

    @prbEntityProperty
    def prbEntity(self):
        return None

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(TrainingSettingsWindow, self)._populate()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__updateVO()

    def _dispose(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__arenasCache.fini()
        super(TrainingSettingsWindow, self)._dispose()

    def getInfo(self):
        if not self.__isCreateRequest:
            self.__settings = self.__settings.fetch(self.prbEntity.getSettings())
        if self.itemsCache.isSynced():
            accountAttrs = self.itemsCache.items.stats.attributes
        else:
            accountAttrs = 0
        _, maxBound = getTrainingBattleRoundLimits(accountAttrs)
        if self.__isEpic:
            rTitle = R.strings.menu.epic_training.create.title() if self.__isCreateRequest else R.strings.menu.epic_training.info.settings.title()
        else:
            rTitle = R.strings.menu.training.create.title() if self.__isCreateRequest else R.strings.menu.training.info.settings.title()
        canChangeComment = isShowComment = self.__isDescriptionEnabled()
        info = {'description': self.__settings.getComment(),
         'timeout': self.__settings.getRoundLen() / 60,
         'arena': self.__settings.getArenaTypeID(),
         'privacy': not self.__settings.isOpened(),
         'create': self.__isCreateRequest,
         'wndTitle': backport.text(rTitle),
         'canMakeOpenedClosed': True,
         'canChangeComment': canChangeComment,
         'isShowComment': isShowComment,
         'canChangeArena': True,
         'maxBattleTime': maxBound / 60}
        if not self.__isCreateRequest:
            permissions = self.prbEntity.getPermissions()
            info['canMakeOpenedClosed'] = permissions.canMakeOpenedClosed()
            info['canChangeComment'] = permissions.canChangeComment() and canChangeComment
            info['canChangeArena'] = permissions.canChangeArena()
        return info

    def updateTrainingRoom(self, arena, roundLength, isPrivate, comment):
        self.__settings.setArenaTypeID(arena)
        self.__settings.setRoundLen(roundLength * 60)
        self.__settings.setOpened(not isPrivate)
        self.__settings.setComment(comment)
        if self.__isEpic:
            eventType = events.TrainingSettingsEvent.UPDATE_EPIC_TRAINING_SETTINGS
        else:
            eventType = events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS
        self.fireEvent(events.TrainingSettingsEvent(eventType, ctx={'settings': self.__settings}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateVO(self):
        self.as_setDataS(self.getInfo(), self.__arenasCache.cache)

    def __onServerSettingsChange(self, diff):
        if self.__INFLUENCING_CONFIG_KEYS.intersection(diff.keys()):
            self.__arenasCache.build()
            self.__updateVO()

    def __isDescriptionEnabled(self):
        return self.__lobbyContext.getServerSettings().preModerationConfig.prebattleDescriptionEnabled
