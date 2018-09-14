# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/Trainings.py
import ArenaType
import MusicController
from adisp import process
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.trainings import formatters
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.prb_control.context.prb_ctx import JoinTrainingCtx, LeavePrbCtx
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.prb_control.prb_helpers import PrbListener
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.utils.functions import getArenaFullName
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.meta.TrainingFormMeta import TrainingFormMeta
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import text_styles
from helpers import i18n

class Trainings(LobbySubView, TrainingFormMeta, PrbListener):

    def __init__(self, _ = None):
        super(Trainings, self).__init__()
        self.__requester = None
        return

    def _populate(self):
        super(Trainings, self)._populate()
        self.startPrbListening()
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_LOBBY)
        self.addListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self.__createTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        self.sendData([], 0)

    def _dispose(self):
        self.stopPrbListening()
        window = self.app.containerManager.getView(ViewTypes.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY})
        if window is not None:
            window.destroy()
        self.removeListener(events.TrainingSettingsEvent.UPDATE_TRAINING_SETTINGS, self.__createTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        super(Trainings, self)._dispose()
        return

    def onLeave(self):
        self.prbDispatcher.doLeaveAction(LeavePrbCtx(waitingID='prebattle/leave'))

    def onWindowMinimize(self):
        g_eventDispatcher.loadHangar()

    def onTryClosing(self):
        self._dispose()
        return True

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)

    def onPrbListReceived(self, prebattles):
        listData = []
        playersTotal = 0
        for item in prebattles:
            arena = ArenaType.g_cache[item.arenaTypeID]
            playersTotal += item.playersCount
            listData.append({'id': item.prbID,
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
            yield g_prbLoader.getDispatcher().create(settings)
        return
