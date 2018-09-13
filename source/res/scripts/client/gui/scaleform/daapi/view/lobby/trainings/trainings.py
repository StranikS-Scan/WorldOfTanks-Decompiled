# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/Trainings.py
import ArenaType
import MusicController
from adisp import process
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.settings import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.trainings import formatters
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.prb_control.functional.training import TrainingListRequester
from gui.prb_control.context.prb_ctx import JoinTrainingCtx
from gui.prb_control.prb_helpers import prbDispatcherProperty
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils.functions import getArenaFullName
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.TrainingFormMeta import TrainingFormMeta
from gui.prb_control.dispatcher import g_prbLoader

class Trainings(LobbySubView, TrainingFormMeta):

    def __init__(self):
        super(Trainings, self).__init__()
        self.app.component.wg_inputKeyMode = 1
        self.__requester = None
        return

    def _populate(self):
        super(Trainings, self)._populate()
        self.__requester = TrainingListRequester()
        self.__requester.start(self.__onTrainingsListReceived)
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_LOBBY)
        self.addListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self.__createTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        if self.__requester is not None:
            self.__requester.stop()
            self.__requester = None
        window = self.app.containerManager.getView(ViewTypes.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.TRAINING_SETTINGS_WINDOW})
        if window is not None:
            window.destroy()
        self.removeListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self.__createTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        super(Trainings, self)._dispose()
        return

    @process
    def __createTrainingRoom(self, event):
        settings = event.ctx.get('settings', None)
        if settings:
            settings.setWaitingID('prebattle/create')
            yield g_prbLoader.getDispatcher().create(settings)
        return

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.ShowViewEvent(events.ShowViewEvent.SHOW_LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    def __onTrainingsListReceived(self, prebattles):
        result = []
        totalPlayersCount = 0
        for item in prebattles:
            arena = ArenaType.g_cache[item.arenaTypeID]
            totalPlayersCount += item.playersCount
            result.append({'id': item.prbID,
             'comment': item.getCensoredComment(),
             'arena': getArenaFullName(item.arenaTypeID),
             'count': item.playersCount,
             'total': arena.maxPlayersInTeam,
             'owner': item.getCreatorFullName(),
             'creatorName': item.creator,
             'creatorClan': item.clanAbbrev,
             'creatorIgrType': item.creatorIgrType,
             'creatorRegion': g_lobbyContext.getRegionCode(item.creatorDbId),
             'icon': formatters.getMapIconPath(arena, prefix='small/'),
             'disabled': not item.isOpened})

        self.as_setListS(result, totalPlayersCount)

    @process
    def joinTrainingRequest(self, prbID):
        yield self.prbDispatcher.join(JoinTrainingCtx(prbID, waitingID='prebattle/join'))

    def createTrainingRequest(self):
        self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_TRAINING_SETTINGS_WINDOW, ctx={'isCreateRequest': True}))
