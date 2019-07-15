# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/trainings_list_base.py
import ArenaType
from adisp import process
from constants import PREBATTLE_MAX_OBSERVERS_IN_TEAM, OBSERVERS_BONUS_TYPES
from helpers import dependency
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.trainings import formatters
from gui.Scaleform.daapi.view.lobby.trainings.sound_constants import TRAININGS_SOUND_SPACE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.TrainingFormMeta import TrainingFormMeta
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.shared.utils.functions import getArenaFullName
from gui.prb_control.entities.base.legacy.listener import ILegacyListener
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.sounds.ambients import LobbySubViewEnv
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.impl import backport
from gui.impl.gen import R
from skeletons.gui.lobby_context import ILobbyContext

class TrainingsListBase(LobbySubView, TrainingFormMeta, ILegacyListener):
    __sound_env__ = LobbySubViewEnv
    _COMMON_SOUND_SPACE = TRAININGS_SOUND_SPACE
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, _=None):
        super(TrainingsListBase, self).__init__()
        self.__requester = None
        return

    def onLeave(self):
        self.__doLeave()

    def onWindowMinimize(self):
        g_eventDispatcher.loadHangar()

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
             'creatorRegion': self._lobbyContext.getRegionCode(item.creatorDbId),
             'icon': formatters.getMapIconPath(arena, prefix='small/'),
             'disabled': not item.isOpened,
             'badgeImgStr': item.getBadgeImgStr()})

        self.sendData(listData, playersTotal)

    def sendData(self, listData, playersTotal):
        result = {'listData': listData,
         'roomsLabel': text_styles.main(backport.text(R.strings.menu.training.roomsLabel(), roomsTotal=text_styles.stats(str(len(listData))))),
         'playersLabel': text_styles.main(backport.text(R.strings.menu.training.playersLabel(), playersTotal=text_styles.stats(str(playersTotal))))}
        self.as_setListS(result)

    def _populate(self):
        super(TrainingsListBase, self)._populate()
        Waiting.show('Flash')
        self.startPrbListening()
        self.__setViewData()
        self.sendData([], 0)

    def _dispose(self):
        if Waiting.isOpened('Flash'):
            Waiting.hide('Flash')
        self.stopPrbListening()
        super(TrainingsListBase, self)._dispose()

    def _getViewData(self):
        raise NotImplementedError('Data should be implemented. Must be overridden in subclass')

    @process
    def _createTrainingRoom(self, event):
        settings = event.ctx.get('settings', None)
        if settings:
            settings.setWaitingID('prebattle/create')
            yield self.prbDispatcher.create(settings)
        return

    def __setViewData(self):
        info = self._getViewData()
        if info:
            self.as_setInfoS(info)

    @process
    def __doLeave(self, isExit=True):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction(isExit=isExit))
