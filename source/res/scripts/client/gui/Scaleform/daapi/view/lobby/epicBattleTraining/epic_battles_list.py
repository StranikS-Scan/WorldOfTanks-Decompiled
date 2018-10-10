# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattleTraining/epic_battles_list.py
import ArenaType
from adisp import process
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.epicBattleTraining import formatters
from gui.Scaleform.daapi.view.meta.TrainingFormMeta import TrainingFormMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.base.legacy.listener import ILegacyListener
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import getArenaFullName
from gui.sounds.ambients import LobbySubViewEnv
from gui.prb_control.entities.epic_battle_training.ctx import EpicTrainingSettingsCtx, JoinEpicBattleTrainingCtx
from helpers import dependency
from helpers import i18n
from skeletons.gui.lobby_context import ILobbyContext

class EpicBattlesList(LobbySubView, TrainingFormMeta, ILegacyListener):
    __sound_env__ = LobbySubViewEnv
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, _=None):
        super(EpicBattlesList, self).__init__()
        self.__requester = None
        return

    def _populate(self):
        super(EpicBattlesList, self)._populate()
        Waiting.show('Flash')
        self.startPrbListening()
        self.addListener(events.TrainingSettingsEvent.UPDATE_EPIC_TRAINING_SETTINGS, self.__createEpicTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        self.sendData([], 0)

    def _dispose(self):
        if Waiting.isOpened('Flash'):
            Waiting.hide('Flash')
        self.stopPrbListening()
        window = self.app.containerManager.getView(ViewTypes.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: PREBATTLE_ALIASES.TRAINING_SETTINGS_WINDOW_PY})
        if window is not None:
            window.destroy()
        self.removeListener(events.TrainingSettingsEvent.UPDATE_EPIC_TRAINING_SETTINGS, self.__createEpicTrainingRoom, scope=EVENT_BUS_SCOPE.LOBBY)
        super(EpicBattlesList, self)._dispose()
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
        yield self.prbDispatcher.join(JoinEpicBattleTrainingCtx(prbID, waitingID='prebattle/join'))

    def createTrainingRequest(self):
        settings = EpicTrainingSettingsCtx()
        gameplayID = ArenaType.getGameplayIDForName('epic')
        geometryID = 96
        arenaTypeID = geometryID | gameplayID << 16
        settings.setArenaTypeID(arenaTypeID)
        settings.setRoundLen(190)
        settings.setOpened(True)
        settings._isRequestToCreate = True
        self.fireEvent(events.TrainingSettingsEvent(events.TrainingSettingsEvent.UPDATE_EPIC_TRAINING_SETTINGS, ctx={'settings': settings}), scope=EVENT_BUS_SCOPE.LOBBY)

    @process
    def __createEpicTrainingRoom(self, event):
        settings = event.ctx.get('settings', None)
        if settings:
            settings.setWaitingID('prebattle/create')
            yield self.prbDispatcher.create(settings)
        return

    @process
    def _doLeave(self, isExit=True):
        yield self.prbDispatcher.doLeaveAction(LeavePrbAction(isExit=isExit))
