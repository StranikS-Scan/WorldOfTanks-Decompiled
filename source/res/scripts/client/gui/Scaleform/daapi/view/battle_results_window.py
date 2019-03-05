# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle_results_window.py
from adisp import process
from gui import SystemMessages
from gui import makeHtmlString
from gui.battle_results.settings import PROGRESS_ACTION
from gui.battle_results import RequestEmblemContext, EMBLEM_TYPE
from gui.prb_control.dispatcher import g_prbLoader
from gui.server_events import events_dispatcher as quests_events
from gui.Scaleform.daapi.view.meta.BattleResultsMeta import BattleResultsMeta
from gui.shared import event_bus_handlers, events, EVENT_BUS_SCOPE
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showProgressiveRewardWindow
from gui.sounds.ambients import BattleResultsEnv
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from soft_exception import SoftException

def _wrapEmblemUrl(emblemUrl):
    return makeHtmlString('html_templates:lobby/battleResult', 'emblemUrl', {'url': emblemUrl})


class BattleResultsWindow(BattleResultsMeta):
    battleResults = dependency.descriptor(IBattleResultsService)
    __sound_env__ = BattleResultsEnv
    __metaclass__ = event_bus_handlers.EventBusListener

    def __init__(self, ctx):
        super(BattleResultsWindow, self).__init__()
        if 'arenaUniqueID' not in ctx:
            raise SoftException('Key "arenaUniqueID" is not found in context', ctx)
        if not ctx['arenaUniqueID']:
            raise SoftException('Value of "arenaUniqueID" must be greater than 0')
        self.__arenaUniqueID = ctx['arenaUniqueID']
        self.__dataSet = False

    def onWindowClose(self):
        self.destroy()

    def showEventsWindow(self, eID, eventType):
        if self.__canNavigate():
            quests_events.showMission(eID, eventType)
            self.destroy()

    def saveSorting(self, iconType, sortDirection, bonusType):
        self.battleResults.saveStatsSorting(bonusType, iconType, sortDirection)

    def getClanEmblem(self, textureID, clanDBID):
        self.__requestClanEmblem(textureID, clanDBID)

    def startCSAnimationSound(self, soundEffectID='cs_animation_league_up'):
        self.app.soundManager.playEffectSound(soundEffectID)

    def showPremiumView(self, data):
        self.as_openPremiumPopoverS(data)

    def onResultsSharingBtnPress(self):
        raise NotImplementedError('This feature is not longer supported')

    def showUnlockWindow(self, itemID, unlockType):
        if not self.__canNavigate():
            return
        if unlockType in (PROGRESS_ACTION.RESEARCH_UNLOCK_TYPE, PROGRESS_ACTION.PURCHASE_UNLOCK_TYPE):
            event_dispatcher.showResearchView(itemID)
            self.onWindowClose()
        elif unlockType == PROGRESS_ACTION.NEW_SKILL_UNLOCK_TYPE:
            event_dispatcher.showPersonalCase(itemID, 2, EVENT_BUS_SCOPE.LOBBY)

    def showProgressiveRewardView(self, data):
        showProgressiveRewardWindow()

    def _populate(self):
        super(BattleResultsWindow, self)._populate()
        if self.battleResults.areResultsPosted(self.__arenaUniqueID):
            self.__setBattleResults()

    @process
    def __requestClanEmblem(self, textureID, clanDBID):
        emblemID = yield self.battleResults.requestEmblem(RequestEmblemContext(EMBLEM_TYPE.CLAN, clanDBID, textureID))
        if not self.isDisposed():
            self.as_setClanEmblemS(textureID, _wrapEmblemUrl(emblemID))

    def __setBattleResults(self):
        if not self.__dataSet:
            battleResultsVO = self.battleResults.getResultsVO(self.__arenaUniqueID)
            self.as_setDataS(battleResultsVO)
            self.__dataSet = True

    @event_bus_handlers.eventBusHandler(events.LobbySimpleEvent.BATTLE_RESULTS_POSTED, EVENT_BUS_SCOPE.LOBBY)
    def __handleBattleResultsPosted(self, event):
        ctx = event.ctx
        if 'arenaUniqueID' not in ctx:
            raise SoftException('Key "arenaUniqueID" is not found in context', ctx)
        if not ctx['arenaUniqueID']:
            raise SoftException('Value of "arenaUniqueID" must be greater than 0')
        if self.__arenaUniqueID == ctx['arenaUniqueID']:
            self.__setBattleResults()

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_BATTLE_RESULT_WINDOW, EVENT_BUS_SCOPE.LOBBY)
    def __handleBattleResultsClose(self, _):
        self.destroy()

    @classmethod
    def __canNavigate(cls):
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled():
            SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error)
            return False
        else:
            return True
