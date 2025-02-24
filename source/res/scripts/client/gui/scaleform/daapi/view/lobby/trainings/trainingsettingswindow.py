# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/TrainingSettingsWindow.py
import ArenaType
from account_helpers import gameplay_ctx
from constants import PREBATTLE_TYPE, Configs
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.Scaleform.daapi.view.meta.TrainingWindowMeta import TrainingWindowMeta
from gui.prb_control import prbEntityProperty
from gui.prb_control.prb_getters import getTrainingBattleRoundLimits
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.utils.functions import getArenaImage
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from gui.training_room_external_handlers import getAllTrainingRoomHandlers, getTrainingRoomHandler
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
CONFIG_KEYS_FOR_UPDATE = {Configs.PRE_MODERATION_CONFIG.value}

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
                 'icon': getArenaImage(arenaType.geometryName),
                 'canChangeArenaTime': not self.__isEpic,
                 'alertText': ''}
                arenaData = self.__getHandlerForArenaTypeName(arenaType.gameplayName).getArenaData()
                if arenaData is not None:
                    dataItem.update(arenaData)
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
        arenaGameplayName = R.strings.arenas.type.dyn(arena.gameplayName).dyn(arena.geometryName)
        return backport.text(arenaGameplayName) if arenaGameplayName.exists() else backport.text(R.strings.arenas.type.dyn(arena.gameplayName).name())

    def __isArenaSuitableForTraining(self, arena):
        if arena.explicitRequestOnly:
            return False
        else:
            arenaTypeFilter = self.__getHandlerForArenaTypeName(arena.gameplayName).getArenaFilter()
            return arenaTypeFilter(arena, self.__settings) if arenaTypeFilter is not None and not self.__isEpic else gameplay_ctx.isCreationEnabled(arena.gameplayName, self.__isEpic)

    def __getHandlerForArenaTypeName(self, arenaTypeName):
        handlers = getAllTrainingRoomHandlers()
        for handler in handlers:
            if handler.isEnabledForGuiTypeName(arenaTypeName):
                return handler

        return getTrainingRoomHandler()


class TrainingSettingsWindow(TrainingWindowMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

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
        minBound, maxBound = getTrainingBattleRoundLimits(accountAttrs)
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
         'minBattleTime': minBound / 60,
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
        if CONFIG_KEYS_FOR_UPDATE.intersection(diff.keys()):
            self.__arenasCache.build()
            self.__updateVO()

    def __isDescriptionEnabled(self):
        return self.__lobbyContext.getServerSettings().preModerationConfig.prebattleDescriptionEnabled
