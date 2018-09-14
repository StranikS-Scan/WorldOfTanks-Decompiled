# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/Trainings.py
import ArenaType
from adisp import process
from constants import PREBATTLE_MAX_OBSERVERS_IN_TEAM, OBSERVERS_BONUS_TYPES, PREBATTLE_TYPE
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.trainings import formatters
from gui.Scaleform.daapi.view.meta.TrainingFormMeta import TrainingFormMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.base.legacy.listener import ILegacyListener
from gui.prb_control.entities.training.legacy.ctx import JoinTrainingCtx
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import getArenaFullName
from gui.sounds.ambients import LobbySubViewEnv
from helpers import dependency
from helpers import i18n
from skeletons.gui.lobby_context import ILobbyContext

class Trainings(LobbySubView, TrainingFormMeta, ILegacyListener):
    __sound_env__ = LobbySubViewEnv
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, _=None):
        super(Trainings, self).__init__()
        self.__requester = None
        return

    def _populate(self):
        super(Trainings, self)._populate()
        funcState = self.prbDispatcher.getFunctionalState()
        if not funcState.isInLegacy(PREBATTLE_TYPE.TRAINING):
            g_eventDispatcher.removeTrainingFromCarousel()
            return
        Waiting.show('Flash')
        self.startPrbListening()
        self.addListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self.__createTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        self.sendData([], 0)

    def _dispose(self):
        if Waiting.isOpened('Flash'):
            Waiting.hide('Flash')
        self.stopPrbListening()
        window = self.app.containerManager.getView(ViewTypes.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY})
        if window is not None:
            window.destroy()
        self.removeListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self.__createTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        super(Trainings, self)._dispose()
        return

    def onLeave(self):
        self._doLeave()

    def onWindowMinimize(self):
        g_eventDispatcher.loadHangar()

    def onTryClosing(self):
        self._dispose()
        return True

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)

    def onLegacyListReceived(self, prebattles):
        if Waiting.isOpened('Flash'):
            Waiting.hide('Flash')
        listData = []
        playersTotal = 0
        addObservers = self.prbEntity.getEntityType() in OBSERVERS_BONUS_TYPES
        for item in prebattles:
            arena = ArenaType.g_cache[item.arenaTypeID]
            playersTotal += item.playersCount
            maxPlayersInTeam = arena.maxPlayersInTeam
            if addObservers:
                maxPlayersInTeam += PREBATTLE_MAX_OBSERVERS_IN_TEAM
            listData.append({'id': item.prbID,
             'comment': item.getCensoredComment(),
             'arena': getArenaFullName(item.arenaTypeID),
             'count': item.playersCount,
             'total': maxPlayersInTeam,
             'owner': item.getCreatorFullName(),
             'creatorName': item.creator,
             'creatorClan': item.clanAbbrev,
             'creatorIgrType': item.creatorIgrType,
             'creatorRegion': self.lobbyContext.getRegionCode(item.creatorDbId),
             'icon': formatters.getMapIconPath(arena, prefix='small/'),
             'disabled': not item.isOpened})

        self.sendData(listData, playersTotal)

    def sendData(self, listData, playersTotal):
        result = {'listData': listData,
         'roomsLabel': text_styles.main(i18n.makeString(MENU.TRAINING_ROOMSLABEL, roomsTotal=text_styles.stats(str(len(listData))))),
         'playersLabel': text_styles.main(i18n.makeString(MENU.TRAINING_PLAYERSLABEL, playersTotal=text_styles.stats(str(playersTotal))))}
        self.as_setListS(result)

    @process
    def joinTrainingRequest(self, prbID):
        yield self.prbDispatcher.join(JoinTrainingCtx(prbID, waitingID='prebattle/join'))

    def createTrainingRequest(self):
        self.fireEvent(events.LoadViewEvent(PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY, ctx={'isCreateRequest': True}), scope=EVENT_BUS_SCOPE.LOBBY)

    @process
    def __createTrainingRoom(self, event):
        settings = event.ctx.get('settings', None)
        if settings:
            settings.setWaitingID('prebattle/create')
            yield self.prbDispatcher.create(settings)
        return

    @process
    def _doLeave(self, isExit=True):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction(isExit=isExit))
